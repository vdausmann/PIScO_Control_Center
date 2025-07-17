from PySide6.QtCore import QObject, Signal, Slot
from .module import Module, ModuleState, Setting
from enum import Enum

class TaskState(Enum):
    """ All possible states of a Task. """
    Idle = 1
    Running = 2
    Finished = 3
    Error = 4

class Task(QObject):

    task_state_changed_signal = Signal(TaskState)
    def __init__(self, name: str, modules: list[Module], state: TaskState):
        super().__init__()
        self.name = name
        self._modules = modules
        self._state = state

        for module in self._modules:
            module.module_state_changed_signal.connect(self.module_state_changed)

    @Slot(ModuleState)
    def module_state_changed(self, _: ModuleState):
        state = TaskState.Finished
        # on state change of one module check the states of all modules and update task
        # state accordingly
        for module in self._modules:
            if module.get_state() == ModuleState.Error: 
                # on one error, the whole task state will be error
                state = TaskState.Error
                break
            if module.get_state() == ModuleState.Running:
                state = TaskState.Running
            if module.get_state() == ModuleState.NotExecuted and state != TaskState.Running:
                state = TaskState.Idle
        self.set_state(state)

    def set_state(self, new_state: TaskState):
        # if the new state differs from the current state, emit signal
        if new_state != self._state:
            self._state = new_state
            self.task_state_changed_signal.emit(self._state)

    def to_dict(self):
        return {"name": self.name, "modules": [m.to_dict() for m in self._modules],
                "state": self._state.name}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data["name"], [Module.from_dict(m) for m in data.get("modules", [])],
                   TaskState[data["state"]])

if __name__ == "__main__":
    import pprint
    s1 = Setting("Setting1", 1, "int")
    s2 = Setting("Setting2", 2, "int")
    m1 = Module("Module1", [s1, s2], [], ModuleState.NotExecuted)
    s3 = Setting("Setting3", 3, "int")
    m2 = Module("Module2", [s1, s2, s3], [], ModuleState.NotExecuted)

    t = Task("TestTask", [m1, m2], TaskState.Idle)
    d = t.to_dict()
    pprint.pp(d)
    d["name"] = "TestTaskFromDict"
    t2 = Task.from_dict(d)
    pprint.pp(t2.to_dict())

    t.task_state_changed_signal.connect(lambda x: print(x.name))
    t.set_state(TaskState.Error)
