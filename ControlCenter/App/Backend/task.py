from .module import Module
from PySide6.QtCore import Signal, QObject
from enum import Enum


class TaskState(Enum):
    """
    All possible states of a Task.
    """

    Inactive = 1
    Active = 2
    Running = 3
    Waiting = 4  # when deactivated but a module is still running
    Finished = 5


class Task(QObject):
    """
    A task is defined as a collection of different modules.
    The tasks runs the modules, handles priorities, communication with other tasks and
    progress tracking.
    """

    changed_state_signal = Signal(TaskState)

    def __init__(
        self, name: str, modules: list[Module], state: TaskState = TaskState.Inactive
    ):
        super().__init__()
        self.modules = modules
        self.name: str = name
        self.state: TaskState = state
        # self.selected_modules = [m.name for m in modules]

    def change_state(self, new_state: TaskState):
        self.state = new_state
        self.changed_state_signal.emit(self.state)

    # def add_module(self, module: Module):
    #     if module.name not in self.selected_modules:
    #         self.modules.append(module)
    #         self.selected_modules.append(module.name)
    #     else:  # module already in this task
    #         print("Module already in module list")
