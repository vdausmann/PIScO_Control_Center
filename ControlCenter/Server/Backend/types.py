from pydantic import BaseModel

STATE_FINISHED = "finished"
STATE_NOTEXECUTED = "not_executed"
STATE_IDLE = "idle"
STATE_RUNNING = "running"
STATE_ERROR = "error"


########################################
## Helper types for initialization
########################################
class ModuleTemplate(BaseModel):
    name: str
    command: list[str]
    num_cores: int
    priority: int
    settings: dict 

class TaskTemplate(BaseModel):
    name: str
    meta_data: dict
    modules: list[ModuleTemplate]

########################################
## Full types used by server and app:
########################################
class Module(BaseModel):
    module_id: str 
    parent_task_id: str 
    name: str
    command: list[str]
    num_cores: int
    priority: int
    settings: dict 
    finished: bool


class Task(BaseModel):
    name: str
    meta_data: dict
    task_id: str
    modules: list[str]

