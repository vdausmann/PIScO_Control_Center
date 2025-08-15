from .setting import Setting
from enum import Enum
from PySide6.QtCore import QObject, Signal

class ModuleState(Enum):
    """ All possible states of a Module. """
    NotExecuted = 1
    Running = 2
    Finished = 3
    Error = 4

class Module(QObject):
    """ Represents a single module which holds all its settings and its current state.
    Emits a signal on state change (only when state is changed via *set_state*
    function). 
    The modules settings are split into Internal and external, where internal settings are
    only for app-handling (like priority and run-command) and external settings are the
    settings used in the external call to the module."""

    module_state_changed_signal = Signal(ModuleState)
    def __init__(self, name: str, external_settings: list[Setting], internal_settings:
                 list[Setting] = [], state: ModuleState = ModuleState.NotExecuted):
        super().__init__()
        self._name = name
        self._external_settings = external_settings
        self._internal_settings = internal_settings
        self._state = state

    def get_state(self):
        return self._state

    def set_state(self, new_value: ModuleState):
        if new_value != self._state:
            self._state = new_value
            self.module_state_changed_signal.emit(self._state)

    def to_dict(self):
        return {"name": self._name, "external_settings": [s.to_dict() for s in
                                                          self._external_settings],
                "internal_settings": [s.to_dict() for s in self._internal_settings],
                "state": self._state.name}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data["name"], [Setting.from_dict(s) for s in data.get("external_settings", [])],
                   [Setting.from_dict(s) for s in data.get("internal_settings", [])],ModuleState[data["state"]])

if __name__ == "__main__":
    import pprint
    s1 = Setting("Setting1", 1, "int")
    s2 = Setting("Setting2", 2, "int")
    is1 = Setting("Priority", 1, "float")
    is2 = Setting("RunCmd", "python3 test.py", "str")

    m = Module("TestModule", [s1, s2], [is1, is2], ModuleState.NotExecuted)
    d = m.to_dict()
    pprint.pp(d)
    m2 = Module.from_dict(d)
    pprint.pp(m2.to_dict())

    m.module_state_changed_signal.connect(lambda x: print(x.name))
    m.set_state(ModuleState.Error)
