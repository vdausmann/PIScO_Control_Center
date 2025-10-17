from pydantic import BaseModel

STATE_FINISHED = "finished"
STATE_NOTEXECUTED = "not_executed"
STATE_IDLE = "idle"
STATE_RUNNING = "running"
STATE_ERROR = "error"


########################################
## Helper types for initialization
########################################

class InternalModuleSettings(BaseModel):
    command: list[str]
    # num_cores: int | str    # use a name (str) to link this to another setting
    num_cores: int | str    # use a name (str) to link this to another setting
    priority: int
    order: int


class ModuleTemplate(BaseModel):
    name: str
    internal_settings: InternalModuleSettings
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
    internal_settings: InternalModuleSettings
    settings: dict 
    finished: bool

    def get_num_cores(self) -> int:
        if type(self.internal_settings.num_cores) == int:
            return self.internal_settings.num_cores
        else:
            return self.settings[self.internal_settings.num_cores]


class Task(BaseModel):
    name: str
    meta_data: dict
    task_id: str
    modules: list[str]
    next_module_to_execute: int


class ChangePropertyRequest(BaseModel):
    property_key: str
    property_value: str | int | float | dict | list | None


