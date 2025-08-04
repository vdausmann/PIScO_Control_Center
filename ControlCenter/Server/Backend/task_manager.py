from pydantic import BaseModel
import uuid


class Module(BaseModel):
    name: str
    num_cores: int = 1
    priority: int = 1
    settings: dict 

class Task(BaseModel):
    name: str
    meta_data: dict
    modules: list[Module]
    # convert to json: task.model_dump_json()


class TaskManager:
    def __init__(self) -> None:
        self.tasks: dict[str, Task] = {}
        self.started_tasks: list[str] = []

    
    def add_task(self, task: Task):
        id = str(uuid.uuid4())
        self.tasks[id] = task
        return id

    def get_task(self, task_id: str):
        if task_id not in self.tasks:
            raise KeyError(f"Task with Id {task_id} not found")
        return self.tasks[task_id]

    def start_task(self, task_id: str):
        self.started_tasks.append(task_id)
        return {"status": "started", "task_id": task_id}
