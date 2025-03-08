from re import sub
from PySide6.QtCore import QThread, Signal, QObject
import subprocess

class Command(QObject):
    terminal_signal = Signal(str, bool, bool)

    def __init__(self, cmd: str, run_thread: QThread, terminal):
        super().__init__()
        self.cmd = cmd
        self.terminal = terminal
        self.run_thread = run_thread
        self.run()

    def run_command(self):
        self.terminal_signal.emit("Starting Command " + " ".join(self.cmd), False, False)
        # process = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
        process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE , stderr=subprocess.PIPE, bufsize=0)

        buffer = ""
        while process.poll() is None:
            s = process.stdout.read(1)
            if s == b"\n":
                self.terminal_signal.emit(buffer, True, False)
                buffer = ""
            elif s == b"\r": 
                self.terminal_signal.emit(buffer, True, True)
                buffer = ""
            elif s == b"\t": 
                buffer += "|    "
            else:
                buffer += s.decode("utf-8")


        out, err = process.communicate()

        self.terminal_signal.emit("Finished Command " + " ".join(self.cmd), False, False)
        if err != b"":
            print(err.decode("utf-8"))
        #     self.terminal_signal.emit("\t Errors: \n" + err.decode("utf-8"), True, False)
        # self.terminal_signal.emit("\t Output: \n" + out.decode("utf-8"), True, False)

        self.run_thread.terminate()

    def run(self):
        self.moveToThread(self.run_thread)
        self.run_thread.started.connect(self.run_command)
        self.terminal_signal.connect(self.terminal.print)

        self.run_thread.start()
