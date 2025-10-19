from PySide6.QtCore import QObject, QProcess, QTimer, Signal
from .ssh_connection import SSHConnectionDialog, SSHConnectionClient
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

        self.ssh_client = SSHConnectionClient()

        self.server_start_timer = QTimer(interval=2000, singleShot=True)

    def start_server(self):
        if self.remote:
            dialog = SSHConnectionDialog(self.ssh_client)
            dialog.exec()
        # if self.server_started:
        #     ...
        # else:
        # if not self.port is None and not self.host is None:
        #     process = QProcess()
        #     process.setProgram("python3")
        #     process.setArguments(
        #             [ "start_server.py",
        #                 "--host", self.host,
        #                 "--port", str(self.port) ])
        #     success = process.startDetached()
        #     self.server_start_started_signal.emit(success)
        #     if success:
        #         self.server_started = True
        #         self.server_start_timer.start()
        #         self.server_start_timer.timeout.connect(lambda: self.server_start_finished_signal.emit())
