from asyncio.subprocess import Process
from fastapi import WebSocket
import uuid
import asyncio

from .communication import error_msg, module_finished_msg, module_started_msg, stdout_msg, stderr_msg
from .types import STATE_FINISHED, STATE_RUNNING, TaskClient, TaskServer, ModuleServer

class TaskManager:
    def __init__(self, connected_clients: list[WebSocket]) -> None:
        self.connected_clients = connected_clients

        self.tasks: dict[str, TaskServer] = {}
        self.modules: dict[str, ModuleServer] = {}

        self.started_tasks: list[str] = [] # [task_id]
        self.running_modules: list[str] = [] # [module_id]
        self.processes: dict[str, Process] = {} # {module_id: process}

        # Settings
        self.max_cores: int = 12

    
    def add_task(self, task: TaskClient) -> TaskClient:
        """Adds a task to the server.

        The client will create tasks using the TaskBase class. These tasks contain
        meta_data and a list of modules. The modules themself are created using the
        ModuleBase class and contain external and internal settings. When uploaded to the
        server, the server will generate ids for the task and each module. The server
        splits the task from the module and references their connection by the ids. For
        better handling on the clients side the id and parent_task_id parameters of the
        task and each module are set by the server and the modified task is returned. The
        client needs the ids to get status updates etc. from the server.
        """

        task_id = str(uuid.uuid4())
        # modify task and modules and split modules from task for serverside handling
        task.task_id = task_id
        modules = []
        for module in task.modules:
            module_id = str(uuid.uuid4())
            module.module_id = module_id
            module.parent_task_id = task_id
            modules.append(module_id)
            self.modules[module_id] = ModuleServer(module_id=module_id,
                                                   parent_task_id=task_id,
                                                   command=module.command,
                                                   num_cores=module.num_cores,
                                                   priority=module.priority,
                                                   settings=module.settings,
                                                   finished=(module.state ==
                                                             STATE_FINISHED),
                                                   error=False
                                                   )
        self.tasks[task_id] = TaskServer(task_id = task_id, modules=modules)
        return task

    def get_task(self, task_id: str):
        if task_id not in self.tasks:
            raise KeyError(f"Task with Id {task_id} not found")
        return self.tasks[task_id]

    def get_module(self, module_id: str):
        if module_id not in self.modules:
            raise KeyError(f"Module with Id {module_id} not found")
        return self.modules[module_id]

    async def _send_message_to_clients(self, msg: dict):
        for ws in self.connected_clients:
            await ws.send_json(msg)


    def _start_task(self, task_id: str):
        self.started_tasks.append(task_id)

    async def watch_processes(self):
        while True:
            if not self.running_modules:
                # No active tasks, sleep and wait for new tasks
                await asyncio.sleep(1)
                continue
    
            to_remove = []
            for module_id in self.running_modules:
                process = self.processes[module_id]
                
                if process.stdout:
                    try: 
                        line = await asyncio.wait_for(process.stdout.readline(),
                                                      timeout=0.1)
                        if line:
                            line = line.decode("utf-8").strip()
                            await self._send_message_to_clients(
                                    stdout_msg(line, module_id, self.modules[module_id].parent_task_id)
                                    )
                    except asyncio.TimeoutError:
                        pass
                    except Exception as e:
                        print(e)
                        pass
                if process.stderr:
                    try: 
                        line = await asyncio.wait_for(process.stderr.readline(),
                                                      timeout=0.1)
                        if line:
                            line = line.decode("utf-8").strip()
                            await self._send_message_to_clients(
                                    stderr_msg(line, module_id, self.modules[module_id].parent_task_id)
                                    )
                    except asyncio.TimeoutError:
                        pass

                ret_code = process.returncode
                if ret_code is not None:
                    # get all remaining output:
                    while True:
                        if process.stdout is not None:
                            stdout_line = await process.stdout.readline()
                        else:
                            stdout_line = bytes()
                        if process.stderr is not None:
                            stderr_line = await process.stderr.readline()
                        else:
                            stderr_line = bytes()
                        if not stdout_line and not stderr_line:
                            break
                        if stdout_line:
                            line = stdout_line.decode("utf-8").strip()
                            await self._send_message_to_clients(stdout_msg(line, module_id, self.modules[module_id].parent_task_id))
                        if stderr_line:
                            line = stderr_line.decode("utf-8").strip()
                            await self._send_message_to_clients(stderr_msg(line, module_id, self.modules[module_id].parent_task_id))

                    self.modules[module_id].finished = True
                    to_remove.append(module_id)
                    await self._send_message_to_clients(
                            module_finished_msg(self.modules[module_id].parent_task_id, module_id, ret_code)
                            )


            for id in to_remove:
                self.running_modules.remove(id)

            await asyncio.sleep(0.1)


    async def _read_stream(self, stream, prefix=""):
        """Reads lines from an asyncio stream and prints them in real-time."""
        while True:
            line_bytes = await stream.readline()
            if not line_bytes: # EOF
                break
            line = line_bytes.decode().strip()
            print(f"[{prefix}]: {line}")

    async def _run_module(self, module_id: str) -> Process | None:
        try:
            module: ModuleServer = self.modules[module_id]
        except KeyError:
            await self._send_message_to_clients(
                    error_msg(404, f"Module with id {module_id} not found!"))
            return None
        try:
            process = await asyncio.create_subprocess_exec(
                    *module.command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
            )

            await self._send_message_to_clients(module_started_msg(process.pid, module.parent_task_id,
                                                                   module.module_id))
            return process

        except FileNotFoundError:
            await self._send_message_to_clients(
                    error_msg(404, f"Command not found: {" ".join(module.command)}",
                                                          module.parent_task_id,
                              module.module_id))
        except Exception as e:
            await self._send_message_to_clients(
                    error_msg(400, f"Unknown exception {e} for command: {" ".join(module.command)}",
                                                          module.parent_task_id,
                              module.module_id))
        return None


    async def _run_next_modules(self):
        current_used_cores = sum([self.modules[id].num_cores for id in self.running_modules])
        possible_modules: list[str] = []

        for task_id in self.started_tasks:
            for module_id in self.tasks[task_id].modules:
                if (module_id not in self.running_modules and not
                    self.modules[module_id].finished and current_used_cores +
                    self.modules[module_id].num_cores <= self.max_cores):
                    possible_modules.append(module_id)

        possible_modules.sort(key=lambda id: self.modules[id].priority)

        while possible_modules and current_used_cores < self.max_cores:
            module_id = possible_modules.pop()
            if self.modules[module_id].num_cores + current_used_cores > self.max_cores:
                break

            # process = asyncio.run(self._run_module(module_id))
            process = await self._run_module(module_id)

            if process is not None:
                current_used_cores += self.modules[module_id].num_cores
                self.processes[module_id] = process
                self.running_modules.append(module_id)


