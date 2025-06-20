from PySide6.QtCore import QObject, Signal, QProcess, QTimer
from .task import Task, TaskState
from .module import Module, ModuleState


class TaskManager(QObject):
    def __init__(self):
        super().__init__()
        self.active_tasks = []
        self.running_tasks = []
        self.running_modules = []

        self.max_running_modules = 1

    def add_task(self, task: Task):
        task.changed_state_signal.connect(self.on_task_state_change)

    def remove_task(self, task: Task):
        task.changed_state_signal.disconnect(self.on_task_state_change)

    def on_task_state_change(self, task_state: TaskState):
        task = self.sender()
        if task_state == TaskState.Active:
            self.active_tasks.append(task)
        elif task_state == TaskState.Inactive:
            if task in self.running_tasks:
                for module in self.running_modules:
                    if module.task == task:
                        module.process.stop()
            self.active_tasks.remove(task)
        self.start_module()

    def on_module_state_change(self, state: ModuleState, text: str):
        module = self.sender()
        if state != ModuleState.Running:
            print("removing module", module.name, state.name, text)
            self.running_modules.remove(module)
        self.start_module()

    def start_module(self):
        active_modules = [
            module
            for t in self.active_tasks
            for module in t.modules
            if module.state == ModuleState.NotExecuted
        ]
        active_modules.sort(key=lambda x: x.priority.value)

        while active_modules and len(self.running_modules) < self.max_running_modules:
            module = active_modules.pop()
            self.running_modules.append(module)
            module.change_state_signal.connect(self.on_module_state_change)
            module.run()
