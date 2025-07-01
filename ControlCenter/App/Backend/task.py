from .module import Module, ModuleState
from PySide6.QtCore import Signal, QObject
from enum import Enum


class TaskState(Enum):
    """
    All possible states of a Task.
    """

    Inactive = 1
    Active = 2
    Running = 3
    Finished = 4


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
        self.progress = 0
        self.running = 0
        for module in self.modules:
            module.change_state_signal.connect(self.on_module_state_change)
            if module.state == ModuleState.Finished:
                self.progress += 1
            if module.state == ModuleState.Running:
                self.running += 1
        # self.selected_modules = [m.name for m in modules]

    def on_module_state_change(self, new_state: ModuleState, text: str):
        self.progress = 0
        self.running = 0
        for module in self.modules:
            if module.state == ModuleState.Finished:
                self.progress += 1
            if module.state == ModuleState.Running:
                self.running += 1

        if self.progress == len(self.modules): 
            # change to finished state if all modules are finished
            self.change_state(TaskState.Finished)
        elif self.running > 0 and self.state != TaskState.Running:
            # change to running state if modules are running and state is not already
            # running
            self.change_state(TaskState.Running)
        elif self.running == 0 and self.state == TaskState.Running:
            # change to active state when either no tasks are running but the current
            # state is still set to running 
            self.change_state(TaskState.Active)
        elif self.progress < len(self.modules) and self.state == TaskState.Finished:
            # change to active when not all states are finished but the state is still set
            # to finished
            self.change_state(TaskState.Active)

    def change_state(self, new_state: TaskState):
        if new_state == TaskState.Inactive and self.state == TaskState.Running:
            for module in self.modules:
                if module.state == ModuleState.Running:
                    module.stop()

        self.state = new_state
        self.changed_state_signal.emit(self.state)

    def add_modules(self, modules: list[Module]):
        for module in modules:
            if module.name not in self.modules:
                self.modules.append(module)
                module.change_state_signal.connect(self.on_module_state_change)
                if module.state == ModuleState.Finished:
                    self.progress += 1
                if module.state == ModuleState.Running:
                    self.running += 1
            else:  
                print("Module already in module list")
