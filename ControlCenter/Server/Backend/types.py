from pydantic import BaseModel

STATE_FINISHED = "finished"
STATE_NOTEXECUTED = "not_executed"
STATE_IDLE = "idle"
STATE_RUNNING = "running"
STATE_ERROR = "error"


class ModuleClient(BaseModel):
    name: str
    command: list[str]
    num_cores: int = 1
    priority: int = 1
    settings: dict 
    state: str = STATE_NOTEXECUTED
    module_id: str | None = None
    parent_task_id: str | None = None


class ModuleServer(BaseModel):
    module_id: str 
    parent_task_id: str 
    command: list[str]
    num_cores: int
    priority: int
    settings: dict 
    finished: bool
    error: bool

class TaskClient(BaseModel):
    name: str
    meta_data: dict
    modules: list[ModuleClient]
    task_id: str | None = None 
    state: str = STATE_IDLE


class TaskServer(BaseModel):
    task_id: str
    modules: list[str]

