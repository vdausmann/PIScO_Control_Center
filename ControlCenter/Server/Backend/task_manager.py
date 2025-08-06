from fastapi import WebSocket
from pydantic import BaseModel
import uuid
import asyncio


class Module(BaseModel):
    name: str
    command: list[str]
    num_cores: int = 1
    priority: int = 1
    settings: dict 

class Task(BaseModel):
    name: str
    meta_data: dict
    modules: list[Module]
    # convert to json: task.model_dump_json()


class TaskManager:
    def __init__(self, connected_clients: list[WebSocket]) -> None:
        self.tasks: dict[str, Task] = {}
        self.started_tasks: list[str] = []
        self.running_modules: list[tuple[str, int]] = [] # [(task_id, module_index)]
        self.max_cores: int = 6
        self.connected_clients = connected_clients
    
    def _add_task(self, task: Task):
        id = str(uuid.uuid4())
        self.tasks[id] = task
        return id

    def _get_task(self, task_id: str):
        if task_id not in self.tasks:
            raise KeyError(f"Task with Id {task_id} not found")
        return self.tasks[task_id]

    async def _start_task(self, task_id: str):
        self.started_tasks.append(task_id)
        await self._run_next_modules() # try to run modules 

    async def _read_stream(self, stream, prefix=""):
        """Reads lines from an asyncio stream and prints them in real-time."""
        while True:
            line_bytes = await stream.readline()
            if not line_bytes: # EOF
                break
            line = line_bytes.decode().strip()
            print(f"[{prefix}]: {line}")

    async def _run_module(self, module: Module, task_id: str) -> int | None:
        try:
            process = await asyncio.create_subprocess_exec(
                    *module.command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
            )
            print(f"Module {module.name} from task [{task_id}] started successfully. PID: {process.pid}")
            # start monitor task:
            for ws in self.connected_clients:
                await ws.send_json({"Msg": "Process started", "PID": process.pid,
                                    "task_id": task_id, "module_name": module.name})
            return process.pid
        except FileNotFoundError:
            return None
        except Exception as e:
            return None


    async def _run_next_modules(self):
        current_used_cores = sum([self.tasks[task_id].modules[index].num_cores for (task_id, index) in self.running_modules])
        possible_modules: list[tuple[str, Module]] = []
        for id in self.started_tasks:
            for m in self.tasks[id].modules:
                if current_used_cores + m.num_cores <= self.max_cores:
                    possible_modules.append((id, m))

        possible_modules.sort(key=lambda m: m[1].priority)
        while possible_modules and current_used_cores < self.max_cores:
            task_id, module = possible_modules.pop()
            if module.num_cores + current_used_cores > self.max_cores:
                break

            # start module
            pid = await self._run_module(module, task_id)
            current_used_cores += module.num_cores
