from asyncio.subprocess import Process
from datetime import datetime
from fastapi import WebSocket
import uuid
import asyncio
from threading import Lock
import json
import os
import tempfile
from pathlib import Path

from .communication import error_msg, module_finished_msg, module_started_msg, save_msg, stdout_msg, stderr_msg, success_msg, task_added_msg, task_property_changed_msg
from .types import TaskTemplate, Module, Task


SAVEFILE = Path(".server_state.json")


class TaskManager:
    def __init__(self, connected_clients: list[WebSocket]) -> None:
        self.connected_clients = connected_clients
        self.loop = None
        self._save_lock = Lock()

        self.tasks: dict[str, Task] = {}
        self.modules: dict[str, Module] = {}

        self.started_tasks: list[str] = [] # [task_id]
        self.running_modules: list[str] = [] # [module_id]
        self.processes: dict[str, Process] = {} # {module_id: process}

        # Settings
        self.max_cores: int = 12

    def set_loop(self):
        """Call this once from inside FastAPI lifespan or startup."""
        self.loop = asyncio.get_running_loop()
    
    async def add_task(self, task: TaskTemplate) -> Task:
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
        modules = []
        for module in task.modules:
            module_id = str(uuid.uuid4())
            modules.append(module_id)
            m = Module(**module.model_dump(), module_id=module_id, parent_task_id=task_id,
                       finished=False) 
            self.modules[module_id] = m

        self.tasks[task_id] = Task(name=task.name, meta_data=task.meta_data, task_id =
                                   task_id, modules=modules, next_module_to_execute=0)
        await self._send_message_to_clients(task_added_msg(task_id))
        await self.save_state()
        return self.tasks[task_id]

    def get_task(self, task_id: str) -> Task:
        if task_id not in self.tasks:
            raise KeyError(f"Task with Id {task_id} not found")
        return self.tasks[task_id]

    def get_module(self, module_id: str) -> Module:
        if module_id not in self.modules:
            raise KeyError(f"Module with Id {module_id} not found")
        return self.modules[module_id]

    def get_multiple_modules(self, *module_ids: str) -> list[Module]:
        modules: list[Module] = []
        for module_id in module_ids:
            if module_id not in self.modules:
                raise KeyError(f"Module with Id {module_id} not found")
            modules.append(self.modules[module_id])
        return modules

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
                
                # check for outputs and errors:
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

                # check for finished processes:
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
            # save if a module finished 
            if to_remove:
                await self.save_state()
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

    def write_input_file(self, module_id: str) -> str:
        file_name = f"{datetime.date}_{module_id}.cfg"
        file_name.replace(" ", "_")

        # write file
        ...

        return file_name

    async def _run_module(self, module_id: str) -> Process | None:
        try:
            module: Module= self.modules[module_id]
        except KeyError:
            await self._send_message_to_clients(
                    error_msg(404, f"Module with id {module_id} not found!"))
            return None
        try:
            # TODO: Write input file from settings
            input_file = ""

            process = await asyncio.create_subprocess_exec(
                    *module.internal_settings.command + [input_file],
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
            )

            await self._send_message_to_clients(module_started_msg(process.pid, module.parent_task_id,
                                                                   module.module_id))
            return process

        except FileNotFoundError:
            await self._send_message_to_clients(
                    error_msg(404, f"Command not found: {" ".join(module.internal_settings.command)}",
                                                          module.parent_task_id,
                              module.module_id))
        except Exception as e:
            await self._send_message_to_clients(
                    error_msg(400, f"Unknown exception {e} for command: {" ".join(module.internal_settings.command)}",
                                                          module.parent_task_id,
                              module.module_id))
        return None


    async def _run_next_modules(self):
        current_used_cores = sum([self.modules[id].get_num_cores() for id in self.running_modules])
        possible_modules: list[str] = []

        for task_id in self.started_tasks:
            for module_id in self.tasks[task_id].modules:
                if (module_id not in self.running_modules and not
                    self.modules[module_id].finished and current_used_cores +
                    self.modules[module_id].get_num_cores() <= self.max_cores):
                    possible_modules.append(module_id)

        possible_modules.sort(key=lambda id: self.modules[id].internal_settings.priority)

        while possible_modules and current_used_cores < self.max_cores:
            module_id = possible_modules.pop()
            if self.modules[module_id].get_num_cores() + current_used_cores > self.max_cores:
                break

            # process = asyncio.run(self._run_module(module_id))
            process = await self._run_module(module_id)

            if process is not None:
                current_used_cores += self.modules[module_id].get_num_cores()
                self.processes[module_id] = process
                self.running_modules.append(module_id)
        await self.save_state()

    def _save_state_sync(self) -> dict:
        """Synchronous file save and validation logic."""
        with self._save_lock:
            # Creating temp file:
            fd, tmp_path = tempfile.mkstemp(dir=".", prefix="state_", suffix=".tmp")
            success = True
            msg = ""
            try:
                data_to_save = {}
                for key in self.tasks.keys():
                    data_to_save[key] = {}
                    data_to_save[key]["task_id"] = self.tasks[key].task_id
                    data_to_save[key]["modules"] = []
                    for module_id in self.tasks[key].modules:
                        data_to_save[key]["modules"].append(self.modules[module_id].model_dump())
                    
                # Saving to temporary file: 
                with os.fdopen(fd, "w") as tmp_file:
                    json.dump(data_to_save, tmp_file)
                    tmp_file.flush()
                    os.fsync(tmp_file.fileno())

                # validating:
                with open(tmp_path, "r") as f:
                    loaded_data = json.load(f)
                if loaded_data != data_to_save:
                    success = False
                    msg = "Validation of save file failed: written data does not match original data."
                else:
                    # Moving temporary file to SAVEFILE
                    os.replace(tmp_path, SAVEFILE)
            except Exception as e:
                success = False
                msg = f"Saving failed: {e}"
            finally:
                if os.path.exists(tmp_path) and tmp_path != SAVEFILE:
                    os.remove(tmp_path)
            return save_msg(success, msg)

    async def save_state(self) -> dict:
        """Async wrapper for saving state without blocking the event loop."""
        result: dict = await asyncio.to_thread(self._save_state_sync)

        # Send WS message in the correct loop
        if self.loop:
            asyncio.run_coroutine_threadsafe(
                self._send_message_to_clients(result),
                self.loop
            )

        return result

    def save_state_sync(self) -> dict:
        """Sync version safe to call from anywhere."""
        result = self._save_state_sync()

        # Send WS message even from sync context
        if self.loop:
            asyncio.run_coroutine_threadsafe(
                self._send_message_to_clients(result),
                self.loop
            )

        return result

    async def change_task_properties(self, task_id: str, property_key: str, property_value) -> dict:
        try:
            if property_key.startswith("meta_data."):
                meta_data_key = property_key.split(".", 1)[1]
                self.tasks[task_id].meta_data[meta_data_key] = property_value
            else:
                if not hasattr(self.tasks[task_id], property_key):
                    return error_msg(404, f"Invalid property key: {property_key}")
                setattr(self.tasks[task_id], property_key, property_value)
            self.save_state_sync()
            await self._send_message_to_clients(task_property_changed_msg(task_id, property_key))
            return success_msg(f"Changed task property of task {task_id}")
        except KeyError:
            return error_msg(404, f"Invalid task id: {task_id}")
        except ValueError:
            return error_msg(404, f"Invalid property value: {property_value}")
        except Exception as e:
            return error_msg(400, f"Unknown exception when changing task property: {e}")

    def change_module_properties(self, module_id: str, property_key: str, property_value) -> dict:
        try:
            # check if module is running or finished:
            if module_id in self.running_modules:
                return error_msg(409, f"Module {module_id} is running and can not be modified.")
            elif self.modules[module_id].finished:
                return error_msg(409, f"Module {module_id} is finished and can not be modified.")
            setattr(self.modules[module_id], property_key, property_value)
            self.save_state_sync()
            return success_msg(f"Changed module property of task {module_id}")
        except KeyError:
            return error_msg(404, f"Invalid property key: {property_key}")
        except ValueError:
            return error_msg(404, f"Invalid property key: {property_key}")
        except Exception as e:
            return error_msg(400, f"Unknown exception when changing task property: {e}")

    def set_module_unfinished(self, module_id: str) -> dict:
        if not self.modules[module_id].finished:
            return error_msg(409, f"Module {module_id} is not finished and can not be set to 'unfinished'.")
        self.modules[module_id].finished = False
        self.save_state_sync()
        return success_msg(f"Changed state of module {module_id} to unfinished.")

