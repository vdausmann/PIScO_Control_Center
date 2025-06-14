from .settings import Setting
from PySide6.QtCore import QThread
from PySide6.QtCore import QObject, Signal, QProcess
from enum import Enum


class ModuleState(Enum):
    """
    All possible states of a Module.
    """

    NotExecuted = 1
    Running = 2
    Finished = 3
    Error = 4


class ExternalProcessWorker(QObject):
    output_received = Signal(str)
    program_error_received = Signal(str)
    process_error_received = Signal(str)
    finished = Signal(int)

    def __init__(self, command: str):
        super().__init__()
        self.command = command
        self.process = QProcess()

        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.errorOccurred.connect(self.handle_process_error)
        self.process.finished.connect(self.handle_finished)

    def run(self, args):
        program = self.command.split(" ")[0]
        args = self.command.split(" ")[1:]
        print(program, args)
        self.process.setProgram(program)
        self.process.setArguments(args)
        self.process.start()

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode()
        self.output_received.emit(data)

    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode()
        self.program_error_received.emit(data)

    def handle_process_error(self, error):
        print("Process error detected:", error)
        self.process_error_received.emit(error)

    def handle_finished(self, exit_code, _):
        self.finished.emit(exit_code)

    def stop(self):
        self.process.kill()


class Module(QObject):
    """
    A module is the collection of a run command calling an external program and the
    corresponding settings.
    """

    change_state_signal = Signal(ModuleState, str)

    def __init__(
        self,
        name: str,
        task,
        settings: list[Setting],
        internal_settings: dict,
        state: ModuleState = ModuleState.NotExecuted,
    ):
        super().__init__()
        self.name = name
        self.task = task
        self.state: ModuleState = state
        self.settings: list[Setting] = settings
        self.internal_settings(internal_settings)

        self.process = ExternalProcessWorker(self.command.value)
        self.process.finished.connect(self.finished)
        self.process.process_error_received.connect(self.error)

    def internal_settings(self, internal_settings: dict):
        self.command = Setting("command", "string", internal_settings["command"])
        if "priority" in internal_settings:
            self.priority = Setting(
                "priority",
                "double",
                float(internal_settings["priority"]),
                "Priority of this module",
            )
        else:
            self.priority = Setting("priority", "float", 1, "Priority of this module")

    def finished(self):
        self.state = ModuleState.Finished
        self.change_state_signal.emit(self.state, "Finished")

    def error(self, error_text):
        self.state = ModuleState.Error
        self.change_state_signal.emit(self.state, error_text)

    def reset(self):
        self.state = ModuleState.NotExecuted
        self.change_state_signal.emit(self.state, "Reset")

    def run(self):
        if self.state != ModuleState.NotExecuted:
            return

        self.worker = QThread()
        self.process.moveToThread(self.worker)
        # create config file etc.
        config_file_name = ""
        self.worker.started.connect(lambda: self.process.run(config_file_name))

        self.process.finished.connect(self.worker.quit)
        self.worker.start()
        print("started module", self.name, "from task", self.task.name)

        self.state = ModuleState.Running
        self.change_state_signal.emit(self.state, "Started")
