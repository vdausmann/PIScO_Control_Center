from PySide6.QtCore import QByteArray, QObject, QProcess, QUrl, QUrlQuery, Slot, Signal, QThread
from PySide6.QtWebSockets import QWebSocket
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QPushButton, QSizePolicy, QTextEdit,
                               QVBoxLayout, QWidget)

from ..helper import LoadingSpinner
from ..styles import get_delete_button_style, get_push_button_style, get_toolbar_style, BG1
                               
from Server.Backend.types import TaskTemplate, Task
import json
import requests
from time import sleep


class ServerConnectWorker(QThread):
    finished_signal = Signal(bool)  

    def __init__(self, callback, remote: bool = False):
        super().__init__()
        self.callback = callback
        self.remote = remote

    def run(self):
        # Blocking function runs here
        try:
            res = self.callback()
            self.finished_signal.emit(res)
        except:
            self.finished_signal.emit(False)


class ServerClient(QObject):
    websocket_message_received_signal = Signal(dict)
    websocket_connected_signal = Signal(bool)
    server_status_changed_signal = Signal(bool)

    def __init__(self):
        super().__init__()
        self.SOCKET_URL = "ws://127.0.0.1:8000/ws"
        self.SERVER_URL = "http://localhost:8000/"
        self.START_SERVER_SCRIPT = "start_server.sh"
        self.remote = False

        self.process = None

        # Socket
        self.socket = QWebSocket()

        # Networking
        self.network = QNetworkAccessManager()

        self.socket.connected.connect(self.on_websocket_connected)
        self.socket.disconnected.connect(self.on_websocket_disconnected)
        self.socket.textMessageReceived.connect(self.on_message)

        self.connected = None

    def check_server(self, timeout: float = 2) -> bool:
        try:
            resp = requests.get(self.SERVER_URL, timeout=timeout)
            return resp.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def start_server(self):
        if self.connected:
            return

        print("Starting server...")
        QProcess.startDetached(
            "bash",
            [self.START_SERVER_SCRIPT],
            "./Server" 
        )
        sleep(2)

    def stop_server(self):
        try:
            self.send_post_request("shutdown", None, None)
        except:
            ...

    def _connect_to_server(self, remote: bool = False) -> bool:
        # check if server is running, if not start a new one: 
        try:
            if not self.check_server(1):
                self.start_server()
            return True
        except:
            return False


    def connect_to_server(self, remote: bool = False):
        self.worker = ServerConnectWorker(self._connect_to_server, remote)
        self.worker.start()
        self.worker.finished_signal.connect(self.connection_finished)

    @Slot(bool)
    def connection_finished(self, success: bool):
        self.worker = None
        if success:
            self.connect_websocket()
            self.websocket_connected_signal.emit(True)
            print("Socket connected")
        else:
            self.websocket_connected_signal.emit(False)

    def disconnect_from_server(self):
        self.socket.close()

    def connect_websocket(self):
        self.socket.open(self.SOCKET_URL)

    @Slot()
    def on_websocket_connected(self):
        self.connected = True
        self.websocket_connected_signal.emit(True)

    @Slot()
    def on_websocket_error(self):
        self.connected = False
        self.websocket_connected_signal.emit(False)

    @Slot()
    def on_websocket_disconnected(self):
        self.connected = False
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


    # def _connect_to_server(self, remote: bool = False) -> bool:
    #     if remote:
    #         # run ssh port-forwarding
    #         # await loop.run_in_executor(None, self._setup_ssh)
    #         ...
    #
    #     # sleep(1)
    #     # check if server is running:
    #     if not self.server_running():
    #         return False
    #     return True


class ServerConnectOverlay(QWidget):
    """Semi-transparent overlay with connect button."""

    def __init__(self, client: ServerClient, parent = None):
        super().__init__(parent)

        self.client = client
        self.client.websocket_connected_signal.connect(self.finished_connection)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("background-color: rgba(255, 255, 255, 10);")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = QLabel("⚠️ Not connected to a server")
        self.label.setStyleSheet("font-size: 25px; color: #456;")

        self.spinner = LoadingSpinner(self)

        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.spinner, alignment=Qt.AlignmentFlag.AlignCenter)

    @Slot(bool)
    def finished_connection(self, success: bool):
        if not success:
            self.label.setText("Connection failed!")

    @Slot(bool)
    def loading(self, run: bool):
        self.spinner.toggle(run)

    def resize_event(self):
        # Ensure overlay always covers the parent
        if self.parent():
            self.resize(self.parent().size())


class ServerViewer(QWidget):
    loading_signal = Signal(bool)

    def __init__(self, client: ServerClient) -> None:
        super().__init__()
        self.client = client
        self.init_ui()

        self.client.websocket_connected_signal.connect(self.websocket_connected)
        # self.client.server_status_changed_signal.connect(self.server_state)
        self.client.websocket_message_received_signal.connect(self.websocket_msg)

    def init_ui(self):
        self.setStyleSheet(get_toolbar_style())
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        label = QLabel("Server")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 25px; color: #456;")
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)


        self.row = QWidget()
        # row.setStyleSheet("border: none;")
        row_layout = QHBoxLayout(self.row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(0)

        server_settings_container = QWidget()
        server_settings_container_layout = QVBoxLayout(server_settings_container)
        server_settings_container_layout.setContentsMargins(2, 0, 2, 2)
        server_settings_container_layout.setSpacing(4)

        server_settings_label = QLabel("Server settings:")
        server_settings_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        server_settings_label.setStyleSheet("border: none;")

        self.server_status_container = QHBoxLayout()
        self.server_status_container.setContentsMargins(0, 0, 0, 0)
        server_status_label = QLabel("Server status: ")
        server_status_label.setStyleSheet("border: none;")
        self.server_status = QLabel("No server found")
        self.server_status.setStyleSheet("color: red; border: none;")
        self.server_status_container.addWidget(server_status_label)
        self.server_status_container.addWidget(self.server_status)


        ########################
        ## Buttons:
        ########################
        self.server_connect_button = QPushButton("Connect to Server")
        self.server_connect_button.setStyleSheet(get_push_button_style())
        self.server_connect_button.setFixedHeight(30)
        self.server_connect_button.clicked.connect(self.connect_to_server)

        self.server_stop_button = QPushButton("Stop Server")
        self.server_stop_button.setStyleSheet(get_delete_button_style())
        self.server_stop_button.setFixedHeight(30)
        self.server_stop_button.clicked.connect(self.client.stop_server)
        self.server_stop_button.setDisabled(True)

        server_settings_container_layout.addWidget(server_settings_label)
        server_settings_container_layout.addLayout(self.server_status_container)
        server_settings_container_layout.addStretch()
        server_settings_container_layout.addWidget(self.server_connect_button)
        server_settings_container_layout.addWidget(self.server_stop_button)



        server_output_container = QWidget()
        server_output_container_layout = QVBoxLayout(server_output_container)
        server_output_container_layout.setContentsMargins(2, 0, 2, 0)
        server_output_container_layout.setSpacing(0)

        server_output_label = QLabel("Websocket Output:")
        server_output_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        server_output_label.setStyleSheet("border: none;")
        self.server_output = QTextEdit()
        self.server_output.setStyleSheet(f"background-color: {BG1}; border: none;")
        self.server_output.setReadOnly(True)
        self.server_output.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        server_output_container_layout.addWidget(server_output_label)
        server_output_container_layout.addWidget(self.server_output)


        row_layout.addWidget(server_settings_container, 1)
        row_layout.addWidget(server_output_container, 1)
        row_layout.addStretch()


        layout.addWidget(label)
        layout.addWidget(self.row, 1)
        layout.addStretch()

    def connect_to_server(self):
        self.loading_signal.emit(True)
        self.client.connect_to_server()

    @Slot(bool)
    def websocket_connected(self, success: bool):
        # self.server_connect_button.setDisabled(success)

        self.server_stop_button.setDisabled(not success)
        if success:
            self.server_connect_button.setText("Disconnect")
            self.server_connect_button.setStyleSheet(get_delete_button_style())
            self.server_connect_button.clicked.disconnect()
            self.server_connect_button.clicked.connect(self.client.disconnect_from_server)

            self.server_status.setText("Connected")
            self.server_status.setStyleSheet("color: green; border: none;")
            self.loading_signal.emit(False)
        else:
            self.server_status.setText("Disconnected")
            self.server_status.setStyleSheet("color: blue; border: none;")
            self.server_output.clear()

            self.server_connect_button.setText("Connect")
            self.server_connect_button.setStyleSheet(get_push_button_style())
            self.server_connect_button.clicked.disconnect()
            self.server_connect_button.clicked.connect(self.connect_to_server)

    # @Slot(bool)
    # def server_state(self, running: bool):
    #     # self.server_start_button.setDisabled(running)
    #     self.server_connect_button.setDisabled(not running)
    #     self.server_stop_button.setDisabled(not running)
    #
    #     if not running:
    #         self.server_status.setText("No server found")
    #         self.server_status.setStyleSheet("color: red; border: none;")
    #         self.server_output.clear()
    #     else:
    #         self.server_status.setText("Disconnected")
    #         self.server_status.setStyleSheet("color: blue; border: none;")
    #         self.server_output.clear()

        # if connected:
        #     self.client.connect_to_server()

    @Slot(dict)
    def websocket_msg(self, msg: dict):
        scrollbar = self.server_output.verticalScrollBar()
        at_bottom = scrollbar.value() == scrollbar.maximum()

        text = ""
        for key in msg:
            if msg[key]:
                text += f"{key}: {msg[key]}    "
        self.server_output.append(text)
        if at_bottom:  
            scrollbar.setValue(scrollbar.maximum())

