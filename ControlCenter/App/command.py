from PySide6.QtCore import QThread, Signal, QObject
import subprocess

class Command(QObject):
    terminal_signal = Signal(str)

    def __init__(self, cmd: str):
        super().__init__()
        self.cmd = cmd

    def run(self):
        # process = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # out, err = process.communicate()

        print("Run command was called")
        self.terminal_signal.emit("Finished Command" + self.cmd)
        # self.terminal_signal.emit("\t Errors: " + err.decode("utf-8"))
        # self.terminal_signal.emit("\t Output: " + out.decode("utf-8"))
        # self.terminal_signal.emit("Running command: " + self.cmd)
