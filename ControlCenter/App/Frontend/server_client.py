from PySide6.QtCore import QByteArray, QObject, QProcess, QTimer, QUrl, QUrlQuery, Slot, Signal, QThread
from PySide6.QtWebSockets import QWebSocket
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from Server.Backend.types import TaskTemplate, ModuleTemplate, Task, Module
import json
import requests


class ServerConnectWorker(QThread):
    finished_signal = Signal(bool)  

    def __init__(self, callback, remote: bool = False):
        super().__init__()
        self.callback = callback
        self.remote = remote

    def run(self):
        # Blocking function runs here
        try:
            result = self.callback()
            self.finished_signal.emit(result)
        except:
            self.finished_signal.emit(False)


class ServerClient(QObject):
    websocket_message_received_signal = Signal(dict)
    server_status_changed_signal = Signal(bool)
    websocket_connected_signal = Signal(bool)

    def __init__(self):
        super().__init__()
        self.SOCKET_URL = "ws://127.0.0.1:8000/ws"
        self.SERVER_URL = "http://localhost:8000/"
        self.START_SERVER_SCRIPT = "start_server.sh"
        self.remote = False
        self._check_server_timer = QTimer()
        self._check_server_timer.timeout.connect(self.check_server)
        self._check_server_timer.start(1000)

        # Socket
        self.socket = QWebSocket()
        # Networking
        self.network = QNetworkAccessManager()

        self.socket.connected.connect(self.on_connected)
        self.socket.disconnected.connect(self.on_disconnected)
        self.socket.textMessageReceived.connect(self.on_message)

        self.connected = None

    @Slot()
    def check_server(self):
        res = self.server_running(0.5)
        if res != self.connected:
            self.connected = res
            self.server_status_changed_signal.emit(self.connected)

    def server_running(self, timeout: float = 2.0) -> bool:
        try:
            resp = requests.get(self.SERVER_URL, timeout=timeout)
            return resp.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def start_server(self):
        print("Starting server...")
        if self.connected:
            return

        print("Starting server...")
        QProcess.startDetached(
            "bash",
            [self.START_SERVER_SCRIPT],
            "./Server" 
        )
        self.worker = ServerConnectWorker(self.server_running)
        self.worker.start()
        self.worker.finished_signal.connect(self.start_server_finished)


    def stop_server(self):
        if not self.server_running():
            return
        self.send_post_request("shutdown", None, None)

    def start_server_finished(self, success: bool):
        print(success)

    def connect_to_server(self, remote: bool = False):
        self.worker = ServerConnectWorker(self._connect_to_server, remote=remote)
        self.worker.start()
        self.worker.finished_signal.connect(self.connection_finished)

    def connection_finished(self, success: bool):
        self.worker = None
        if success:
            self.connect_websocket()
        else:
            self.websocket_connected_signal.emit(False)

    def disconnect_from_server(self):
        self.socket.close()

    def connect_websocket(self):
        self.socket.open(self.SOCKET_URL)

    @Slot()
    def on_connected(self):
        self.websocket_connected_signal.emit(True)

    @Slot()
    def on_error(self):
        self.websocket_connected_signal.emit(False)

    @Slot()
    def on_disconnected(self):
        self.websocket_connected_signal.emit(False)

    @Slot(dict)
    def on_message(self, msg: str):
        try:   
            # convert JSON to dict
            data = json.loads(msg)  
            self.websocket_message_received_signal.emit(data)
        except json.JSONDecodeError:
            pass

    def on_request_finished(self, reply: QNetworkReply, callback = None):
        if reply.error():
            data = ""
            success = False
        else:
            data = reply.readAll().data().decode()
            success = True

        if callback:
            callback(data, success)
        
        reply.deleteLater()

    def send_get_request(self, req: str, req_key: str, req_value: str, callback: None):
        url = QUrl(f"{self.SERVER_URL}/{req}")
        query = QUrlQuery()
        query.addQueryItem(req_key, req_value)
        url.setQuery(query)

        request = QNetworkRequest(url)
        reply = self.network.get(request)
        reply.finished.connect(callback)

    def send_post_request(self, req: str, req_data: bytes | None, callback: None):
        url = QUrl(f"{self.SERVER_URL}/{req}")
        request = QNetworkRequest(url)
        request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")

        if req_data:
            data = QByteArray(req_data)
        else:
            data = QByteArray()

        reply = self.network.post(request, data)
        reply.finished.connect(callback)


    def add_task_to_server(self, task: TaskTemplate) -> Task | None:
        if not self.connected:
            return
        resp = requests.post(self.SERVER_URL + "add-task", json=task.model_dump())
        if resp.status_code == 200:
            res = resp.json()
            return res

    def get_task_from_server(self, task_id: str) -> Task | None:
        if not self.connected:
            return
        resp = requests.get(self.SERVER_URL + f"get-task/{task_id}")
        if resp.status_code == 200:
            res = resp.json()
            return res

    def get_all_tasks_from_server(self) -> list[Task] | None:
        if not self.connected:
            return
        resp = requests.get(self.SERVER_URL + f"get-all-tasks")
        if resp.status_code == 200:
            res = resp.json()
            res = [Task(**task) for task in res]
            return res


    def _connect_to_server(self, remote: bool = False) -> bool:
        if remote:
            # run ssh port-forwarding
            # await loop.run_in_executor(None, self._setup_ssh)
            ...

        # sleep(1)
        # check if server is running:
        if not self.server_running():
            return False
        return True


