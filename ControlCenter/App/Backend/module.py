from enum import Enum
from PySide6.QtCore import QThread
from PySide6.QtCore import QObject, Signal, QProcess
from .settings import Setting, StringSetting, DoubleSetting, IntSetting


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
        self.process.readyReadStandardError.connect(self.handle_program_error)
        self.process.errorOccurred.connect(self.handle_process_error)
        self.process.finished.connect(self.handle_finished)

    def run(self, args):
        program = self.command.split(" ")[0]
        args = self.command.split(" ")[1:]
        self.process.setProgram(program)
        self.process.setArguments(args)
        self.process.start()

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode()
        self.output_received.emit(data)

    def handle_program_error(self):
        data = self.process.readAllStandardError().data().decode()
        self.program_error_received.emit(data)

    def handle_process_error(self, error):
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
    output_received_signal = Signal(str)

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
        self.output: list[str] = []
        self.process = None
        self.worker = None


    def internal_settings(self, internal_settings: dict):
        self.command = StringSetting(
            "command",
            internal_settings["command"],
            f"Command to run module {self.name}",
        )
        priority = 1
        if "priority" in internal_settings:
            priority = float(internal_settings["priority"])
        self.priority = DoubleSetting(
            "priority",
            priority,
            "Priority of this module",
        )
        self.num_cores: int = 1
        if "nCores" in internal_settings:
            if type(internal_settings["nCores"]) is str:
                for setting in self.settings:
                    if setting.name == internal_settings["nCores"] and type(setting) is IntSetting:
                        setting.value_changed_signal.connect(self.set_num_cores)
                        self.num_cores = setting.value
                        break
            else:
                self.num_cores = internal_settings["nCores"]

    def set_num_cores(self, value: int):
        self.num_cores = value

    def finished(self):
        # The process finishes even if it crashed, in this case don't overwrite the state
        # to finished
        if self.state == ModuleState.Error: 
            return

        self.state = ModuleState.Finished
        self.change_state_signal.emit(self.state, "Finished " + self.name + " " +
                                      self.task.name)

    def process_error(self, error_text):
        self.state = ModuleState.Error
        self.change_state_signal.emit(self.state, error_text)

    def program_error(self, error_text):
        self.output.append("Program error: " + error_text)
        self.output_received_signal.emit("Program error: " + error_text)

    def output_received(self, output: str):
        self.output.append(output)
        self.output_received_signal.emit(output)

    def reset(self):
        if self.state == ModuleState.Running:
            return
        if self.worker is not None:
            self.worker.quit()

        self.state = ModuleState.NotExecuted
        self.change_state_signal.emit(self.state, "Reset: " + self.name)

    def stop(self):
        if self.process is not None:
            self.process.stop()

    def run(self):
        if self.state != ModuleState.NotExecuted:
            return

        self.process = ExternalProcessWorker(self.command.value)

        # connect process signals
        self.process.finished.connect(self.finished)
        self.process.process_error_received.connect(self.process_error)
        self.process.program_error_received.connect(self.program_error)
        self.process.output_received.connect(self.output_received)

        self.worker = QThread()
        self.process.moveToThread(self.worker)

        # create config file etc.
        config_file_name = ""

        self.worker.started.connect(lambda: self.process.run(config_file_name))

        self.process.finished.connect(self.worker.quit)
        self.process.process_error_received.connect(self.worker.quit)

        self.worker.start()

        self.state = ModuleState.Running
        self.change_state_signal.emit(self.state, "Started: " + self.name)
