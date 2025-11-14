from PySide6.QtCore import QByteArray, QObject, QProcess, QTimer, QUrl, Signal
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PySide6.QtWidgets import QMessageBox
import json

from .ssh_connection import SSHConnectionClient


class ServerClient(QObject):
    server_start_started_signal = Signal(bool)
    server_start_finished_signal = Signal()
    request_finished_signal = Signal(object)


    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.manager = QNetworkAccessManager(self)
        self.manager.finished.connect(self._on_request_finished)

        self.server_started: bool = False
        self.host: str | None = "127.0.0.1"
        self.port: int | None = 8000
        self.remote: bool = False
        self.path_to_server_script: str = ""

        self.ssh_client = SSHConnectionClient()

        self.server_start_timer = QTimer(interval=2000, singleShot=True)

    def send_get_request(self, url: str, headers: dict | None = None) -> bool:
        """Perform a GET request."""
        if not self.server_started:
            return False
        
        print("Running", url)
        request = QNetworkRequest(QUrl(url))
        if headers:
            for key, value in headers.items():
                request.setRawHeader(key.encode(), value.encode())

        self.reply = self.manager.get(request)
        self.reply.errorOccurred.connect(self._on_request_error)
        return True

    def send_post_request(self, url: str, data=None, headers: dict | None = None) -> bool:
        """Perform a POST request with optional JSON or raw data."""
        if not self.server_started:
            return False

        request = QNetworkRequest(QUrl(url))
        if headers:
            for key, value in headers.items():
                request.setRawHeader(key.encode(), value.encode())

        # Automatically detect if data is dict -> send JSON
        if isinstance(data, dict):
            request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")
            payload = QByteArray(json.dumps(data).encode())
        elif isinstance(data, (str, bytes)):
            payload = QByteArray(data.encode() if isinstance(data, str) else data)
        else:
            payload = QByteArray()

        self.reply = self.manager.post(request, payload)
        self.reply.errorOccurred.connect(self._on_request_error)
        return True

    def get_url(self):
        return f"http://{self.host}:{self.port}"

    def _on_request_finished(self, reply: QNetworkReply):
        """Handle finished request"""
        data = bytes(reply.readAll().data())
        content_type = reply.header(QNetworkRequest.KnownHeaders.ContentTypeHeader)
        status_code = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)

        result = {
            "status": int(status_code) if status_code else None,
            "content_type": content_type,
            "data": None,
            "error": None,
        }

        try:
            if content_type and "application/json" in content_type.lower():
                result["data"] = json.loads(data.decode())
            else:
                result["data"] = data
        except Exception as e:
            result["error"] = str(e)

        print(result)
        reply.deleteLater()
        self.request_finished_signal.emit(result)

    def _on_request_error(self, code):
        """Handle request error"""
        ...

    def close(self):
        self.ssh_client.close()

    def stop_server(self):
        url = self.get_url() + "/shutdown"
        self.send_post_request(url)

    def ping_server(self):
        url = self.get_url() + "/"
        self.send_get_request(url)

    def start_server(self):
        if self.server_started:
            QMessageBox.information(None, "Server info", "Server already running.")
            return

        if self.port is None or self.host is None:
            return

        if self.remote:
            # command = f"nohup {self.path_to_server_script} --host {self.host} --port {self.port} > /dev/null >2&1 &"
            command = f"{self.path_to_server_script} --host {self.host} --port {self.port} > /dev/null 2>&1 & disown"
            print("starting command", command)
            success, stdout, stderr = self.ssh_client.run_command(command)
            if not success:
                print("SSH command could not be run")
            else:
                print("finished command.")
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

