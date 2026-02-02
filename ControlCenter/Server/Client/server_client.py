import os
from pathlib import Path
import socket
from typing import Optional
from PySide6.QtCore import QByteArray, QObject, QProcess, QTimer, QUrl, Signal
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PySide6.QtWebSockets import QWebSocket
from PySide6.QtWidgets import QMessageBox
import json

import requests

from .ssh_connection import SSHConnectionClient


class ServerClient(QObject):
    start_up_signal = Signal()
    server_started = Signal(bool)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.manager = QNetworkAccessManager(self)

        self.websocket = QWebSocket()
        self.websocket.disconnected.connect(self.on_disconnected)

        self.server_running: bool = False
        self.host: str | None = "127.0.0.1"
        self.port: int | None = 8001
        self.remote: bool = False
        self.path_to_server_script: str = ""

        self.ssh_client = SSHConnectionClient()

        self.start_up_timer = QTimer(interval=1000)
        self.start_up_counter = 0
        self.max_start_up_tries = 20
        self.start_up_timer.timeout.connect(self.server_start_up)

    def get_url(self):
        return f"http://{self.host}:{self.port}"

    def get_request(self, url: str):
        request = QNetworkRequest(QUrl(url))
        reply = self.manager.get(request)
        return reply

    def post_request(self, url: str, payload: Optional[dict] = None):
        request = QNetworkRequest(QUrl(url))
        if not payload is None:
            request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")
            data = json.dumps(payload).encode()
        else:
            data = QByteArray()
        reply = self.manager.post(request, data)
        return reply

    def close(self):
        self.disconnect_from_server()
        self.ssh_client.close()

    def stop_server(self):
        url = self.get_url() + "/shutdown"
        self.post_request(url)
        self.server_running = False
        self.server_started.emit(False)

    def start_server(self):
        if self.server_running:
            QMessageBox.information(None, "Server info", "Server already running.")
            return

        self.start_up_signal.emit()

        if self.port is None or self.host is None:
            return

        if self.remote:
            # command = f"nohup {self.path_to_server_script} --host {self.host} --port {self.port} > /dev/null >2&1 &"
            command = f"{self.path_to_server_script} --host {self.host} --port {self.port} > /dev/null >2&1 & disown"
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

        if success:
            self.start_up_timer.start()

    def check_server(self) -> bool:
        if self.port is None or self.host is None:
            raise ValueError("Can not check server if port or host is not set")
        try:
            with socket.create_connection((self.host, self.port), timeout=0.5):
                return True
        except OSError:
            return False


    def server_start_up(self):
        if self.start_up_counter >= self.max_start_up_tries:
            self.server_started.emit(False)
            self.start_up_timer.stop()
            self.start_up_counter = 0
        running = self.check_server()
        if running:
            self.start_up_timer.stop()
            self.connect_to_server()
            self.server_started.emit(True)
            self.start_up_counter = 0
        else:
            self.start_up_counter += 1

    def connect_to_server(self):
        # connect websocket
        self.websocket.open(QUrl("ws://127.0.0.1:8000/ws"))
        self.server_running = True

    def reconnect_to_server(self):
        running = self.check_server()
        if running:
            self.connect_to_server()
            self.server_started.emit(True)
        else:
            self.server_started.emit(False)

    def disconnect_from_server(self):
        self.websocket.close()

    def on_disconnected(self):
        self.websocket.deleteLater()

    def ping_server(self):
        url = self.get_url() + "/"
        return self.get_request(url)

    def get_data_from_reply(self, reply: QNetworkReply) -> dict:
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
        return result

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

    def open_hdf_file(self, path):
        return self.post_request(self.get_url() + "/open-hdf5-file/" + path)

    def get_hdf_file_group_structure(self, path):
        return self.get_request(self.get_url() + "/get-group-structure/" + path)

    def get_hdf_file_full_structure(self, path):
        return self.get_request(self.get_url() + "/get-full-path/" + path)

    def get_hdf_file_data(self, path):
        return self.get_request(self.get_url() + "/get-data/" + path)

    def get_hdf_file_attributes(self, path):
        return self.get_request(self.get_url() + "/get-attributes/" + path)

    # def get_hdf_file_structure(self, path: str):
    #     return self.get_request(self.get_url() + "/get-hdf5-file-structure/" + path)

