import os
from pathlib import Path
from PySide6.QtCore import QByteArray, QObject, QProcess, QTimer, QUrl, Signal, Slot
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PySide6.QtWidgets import QMessageBox
import json

from .ssh_connection import SSHConnectionClient


class ServerClient(QObject):
    server_started_signal = Signal(bool)
    request_finished_signal = Signal(object)
    server_status_signal = Signal(bool)


    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.manager = QNetworkAccessManager(self)
        self.manager.finished.connect(self._on_request_finished)

        self.server_running: bool = False
        self.host: str | None = "127.0.0.1"
        self.port: int | None = 8000
        self.remote: bool = False
        self.path_to_server_script: str = ""

        self.ssh_client = SSHConnectionClient()

        self.server_start_timer = QTimer(interval=5000, singleShot=True)
        self.server_ping_timer = QTimer()
        self.server_ping_timer.timeout.connect(self._check_server)

    def send_get_request(self, url: str, headers: dict | None = None):
        """Perform a GET request."""
        request = QNetworkRequest(QUrl(url))
        if headers:
            for key, value in headers.items():
                request.setRawHeader(key.encode(), value.encode())

        reply = self.manager.get(request)
        # reply.errorOccurred.connect(self._on_request_error)
        return reply

    def send_post_request(self, url: str, data=None, headers: dict | None = None):
        """Perform a POST request with optional JSON or raw data."""
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

        reply = self.manager.post(request, payload)
        # reply.errorOccurred.connect(self._on_request_error)
        return reply

    def get_url(self):
        return f"http://{self.host}:{self.port}"

    def _change_server_status(self, new_status: bool):
        old_status = self.server_running
        self.server_running = new_status

        if new_status != old_status:
            self.server_status_signal.emit(new_status)

    @Slot(QNetworkReply)
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

        if reply.error() == QNetworkReply.NetworkError.RemoteHostClosedError:
            self._change_server_status(False)
        else:
            self._change_server_status(True)

        try:
            if content_type and "application/json" in content_type.lower():
                result["data"] = json.loads(data.decode())
            else:
                result["data"] = data
        except Exception as e:
            result["error"] = str(e)

        # reply.deleteLater()
        # self.request_finished_signal.emit(result)

    def get_data_from_reply(self, reply: QNetworkReply):
        data = bytes(reply.readAll().data())
        content_type = reply.header(QNetworkRequest.KnownHeaders.ContentTypeHeader)
        status_code = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)

        result = {
            "status": int(status_code) if status_code else None,
            "content_type": content_type,
            "data": None,
            "error": None,
        }

        if reply.error() == QNetworkReply.NetworkError.RemoteHostClosedError:
            self._change_server_status(False)
        else:
            self._change_server_status(True)

        try:
            print("here", content_type, data)
            if content_type and "application/json" in content_type.lower():
                print("decoding:")
                print(data.decode())
                result["data"] = json.loads(data.decode())
            else:
                result["data"] = data
        except Exception as e:
            result["error"] = str(e)

        reply.deleteLater()
        return result

    def _on_request_error(self, code):
        """Handle request error"""
        print("Error:", code)

    def close(self):
        self.ssh_client.close()

    def stop_server(self):
        url = self.get_url() + "/shutdown"
        self.send_post_request(url)
        self.server_status_signal.emit(False)
        self.server_ping_timer.stop()
        self.server_running = False

    def ping_server(self):
        url = self.get_url() + "/"
        return self.send_get_request(url)

    def start_server(self):
        if self.server_running:
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
        self.connect_to_server(success)

    def connect_to_server(self, success: bool):
        self.server_started_signal.emit(success)
        if success:
            self.server_ping_timer.start(2000)

    def _check_server(self):
        reply = self.ping_server()

    def list_dir(self, path=None):
        if not self.server_running:
            raise ValueError("Requested list_dir from server which is not running")
        if self.remote:
            return self.ssh_client.listdir(path)
        else:
            if path is None:
                path = Path.home()
            out = []
            entries = os.listdir(path)
            for entry in entries:
                out.append((entry, os.path.join(path, entry),
                            os.path.isdir(os.path.join(path, entry))))
            return out

    def reconnect(self):
        if self.server_running:
            return
        self._check_server()
        print(self.server_running)
        self.connect_to_server(self.server_running)


    def open_hdf_file(self, file_path: str):
        url = self.get_url() + f"/open-hdf5-file/{file_path}"
        return self.send_post_request(url)

    def get_hdf_file_path(self, file_path: str):
        url = self.get_url() + f"/get-hdf5-file-data/{file_path}"
        return self.send_get_request(url)
