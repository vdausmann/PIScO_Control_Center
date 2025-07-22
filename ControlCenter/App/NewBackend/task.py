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
    task_delete_signal = Signal()
    task_modules_changed_signal = Signal()
    task_meta_data_changed_signal = Signal()
    def __init__(self, name: str, modules: list[Module], state: TaskState, meta_data: dict):
        super().__init__()
        self.name = name
        self._modules = modules
        self._state = state
        self._meta_data = meta_data

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

    def get_state(self):
        return self._state

    def delete(self):
        self.task_delete_signal.emit()

    def add_module(self, new_module: Module):
        new_module.module_state_changed_signal.connect(self.module_state_changed)
        self._modules.append(new_module)
        self.task_modules_changed_signal.emit()

    def remove_module(self, module: Module):
        module.module_state_changed_signal.disconnect(self.module_state_changed)
        self._modules.remove(module)
        self.task_modules_changed_signal.emit()

    def edit_meta_data(self, key: str, val, delete: bool = False):
        if key in self._meta_data.keys() and delete:
            self._meta_data.pop(key)
        else:
            self._meta_data[key] = val
        self.task_meta_data_changed_signal.emit()

    def to_dict(self):
        return {"name": self.name, "modules": [m.to_dict() for m in self._modules],
                "state": self._state.name, "meta_data": self._meta_data}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data["name"], [Module.from_dict(m) for m in data.get("modules", [])],
                   TaskState[data["state"]], data["meta_data"])

def get_test_task(name: str = "TestTask", three_modules: bool = False):
    s1 = Setting("Setting1", 1, "int")
    s2 = Setting("Setting2", 2, "int")
    m1 = Module("Module1", [s1, s2], [], ModuleState.NotExecuted)
    s3 = Setting("Long name Setting3", "Test", "str")
    m2 = Module("Module2", [s1, s2, s3], [], ModuleState.NotExecuted)
    if three_modules:
        m3 = Module("Module3", [s1], [], ModuleState.NotExecuted)
        t = Task(name, [m1, m2, m3], TaskState.Idle)
    else:
        t = Task(name, [m1, m2], TaskState.Idle)
    return t

if __name__ == "__main__":
    import pprint
    s1 = Setting("Setting1", 1, "int")
    s2 = Setting("Setting2", 2, "int")
    m1 = Module("Module1", [s1, s2], [], ModuleState.NotExecuted)
    s3 = Setting("Setting3", "Test", "str")
    m2 = Module("Module2", [s1, s2, s3], [], ModuleState.NotExecuted)

    t = Task("TestTask", [m1, m2], TaskState.Idle)
    d = t.to_dict()
    pprint.pp(d)
    d["name"] = "TestTaskFromDict"
    t2 = Task.from_dict(d)
    pprint.pp(t2.to_dict())

    t.task_state_changed_signal.connect(lambda x: print(x.name))
    t.set_state(TaskState.Error)
