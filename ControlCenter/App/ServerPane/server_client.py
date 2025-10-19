from PySide6.QtCore import QObject, QProcess, QTimer, Signal
from paramiko import common
from .ssh_connection import SSHConnectionClient
import paramiko


class ServerClient(QObject):
    server_start_started_signal = Signal(bool)
    server_start_finished_signal = Signal()


    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.server_started: bool = False
        self.host: str | None = "127.0.0.1"
        self.port: int | None = 8000
        self.remote: bool = False
        self.path_to_server_script: str = ""

        self.ssh_client = SSHConnectionClient()

        self.server_start_timer = QTimer(interval=2000, singleShot=True)

    def close(self):
        self.ssh_client.close()

    def start_server(self):
        if self.server_started:
            ...
        else:
            if self.port is None or self.host is None:
                return

            if self.remote:
                command = f"nohup python3 {self.path_to_server_script} --host {self.host} --port {self.port} > /dev/null >2&1 &"
                stdout, stderr = self.ssh_client.run_command(command)
                s = ""
                for line in stdout:
                    s+=line.strip()
                print(s)
                s = ""
                for line in stderr:
                    s+=line.strip()
                print(s)
            else:
                process = QProcess()
                process.setProgram("python3")
                process.setArguments(
                        [ "start_server.py",
                            "--host", self.host,
                            "--port", str(self.port) ])
                success = process.startDetached()
                self.server_start_started_signal.emit(success)
                if success:
                    self.server_started = True
                    self.server_start_timer.start()
                    self.server_start_timer.timeout.connect(lambda: self.server_start_finished_signal.emit())
