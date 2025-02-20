from PySide6.QtCore import QThread, Signal, QObject
import subprocess
import time

class Command(QObject):
    terminal_signal = Signal(str)

    def __init__(self, cmd: str, run_thread: QThread, terminal):
        super().__init__()
        self.cmd = cmd
        self.terminal = terminal
        self.run_thread = run_thread
        self.run()

    def run_this_command(self):
        self.terminal_signal.emit("Starting Command " + self.cmd)
        process = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()

        self.terminal_signal.emit("Finished Command " + self.cmd)
        self.terminal_signal.emit("\t Errors: " + err.decode("utf-8"))
        self.terminal_signal.emit("\t Output: " + out.decode("utf-8"))
        self.terminal_signal.emit("Running command: " + self.cmd)

        self.run_thread.terminate()

    def run(self):
        self.moveToThread(self.run_thread)
        self.run_thread.started.connect(self.run_this_command)
        self.terminal_signal.connect(self.terminal.print)

        self.run_thread.start()
