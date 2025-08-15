from PySide6.QtWidgets import (QHBoxLayout, QLabel, QPushButton, QSizePolicy, QTextEdit, QVBoxLayout, QWidget,
                               QGraphicsBlurEffect, QFrame)
from PySide6.QtCore import Qt, Signal, Slot
from pydantic import main

from .styles import BORDER, get_delete_button_style, get_main_window_style, get_push_button_style, get_toolbar_style, BG1
from .server_client import ServerClient
from .task_view_object import TaskViewObject
from .helper import LoadingSpinner
from Server.Backend.types import Task




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

        self.connect_button = QPushButton("Connect to server")
        self.connect_button.setStyleSheet(get_push_button_style())
        self.connect_button.clicked.connect(self.connect_button_callback)
        self.connect_button.setFixedHeight(30)
        self.connect_button.setFixedWidth(160)


        self.start_server_button = QPushButton("Start server")
        self.start_server_button.setStyleSheet(get_push_button_style())
        self.start_server_button.clicked.connect(self.start_server_button_callback)
        self.start_server_button.setFixedHeight(30)
        self.start_server_button.setFixedWidth(160)

        self.spinner = LoadingSpinner()

        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.connect_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.start_server_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.spinner, alignment=Qt.AlignmentFlag.AlignCenter)


    @Slot()
    def connect_button_callback(self):
        self.spinner.toggle(True)
        self.client.connect_to_server()
        self.label.setText("Connecting to server...")

    @Slot()
    def start_server_button_callback(self):
        self.spinner.toggle(True)
        self.client.start_server()
        self.label.setText("Starting Server...")

    @Slot(bool)
    def finished_connection(self, success: bool):
        self.spinner.toggle(False)
        if not success:
            self.label.setText("Connection failed!")
            self.connect_button.setText("Retry")

    def resize_event(self):
        # Ensure overlay always covers the parent
        if self.parent():
            self.resize(self.parent().size())


class ServerViewer(QWidget):

    def __init__(self, client: ServerClient) -> None:
        super().__init__()
        self.client = client
        self.init_ui()

        self.client.websocket_connected_signal.connect(self.websocket_connected)
        self.client.server_status_changed_signal.connect(self.server_state)
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


        row = QWidget()
        # row.setStyleSheet("border: none;")
        row_layout = QHBoxLayout(row)
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
        self.server_status = QLabel("Not connected to a server")
        self.server_status.setStyleSheet("color: red; border: none;")
        self.server_status_container.addWidget(server_status_label)
        self.server_status_container.addWidget(self.server_status)


        ########################
        ## Buttons:
        ########################
        self.server_connect_button = QPushButton("Connect to Server")
        self.server_connect_button.setStyleSheet(get_push_button_style())
        self.server_connect_button.clicked.connect(self.client.connect_to_server)
        self.server_connect_button.setDisabled(True)

        self.server_start_button = QPushButton("Start Server")
        self.server_start_button.setStyleSheet(get_push_button_style())
        self.server_start_button.clicked.connect(self.client.start_server)
        self.server_start_button.setDisabled(True)

        self.server_stop_button = QPushButton("Stop Server")
        self.server_stop_button.setStyleSheet(get_delete_button_style())
        self.server_stop_button.clicked.connect(self.client.stop_server)
        self.server_stop_button.setDisabled(True)


        server_settings_container_layout.addWidget(server_settings_label)
        server_settings_container_layout.addLayout(self.server_status_container)
        server_settings_container_layout.addStretch()
        server_settings_container_layout.addWidget(self.server_connect_button)
        server_settings_container_layout.addWidget(self.server_start_button)
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
        layout.addWidget(row, 1)
        layout.addStretch()

    @Slot(bool)
    def websocket_connected(self, success: bool):
        if success:
            ...
        else:
            self.server_output.clear()

    @Slot(bool)
    def server_state(self, connected: bool):
        self.server_start_button.setDisabled(connected)
        self.server_connect_button.setDisabled(not connected)
        self.server_stop_button.setDisabled(not connected)

    @Slot(dict)
    def websocket_msg(self, msg: dict):
        scrollbar = self.server_output.verticalScrollBar()
        at_bottom = scrollbar.value() == scrollbar.maximum()

        text = ""
        for key in msg:
            text += f"{key}: {msg[key]}    "
        self.server_output.append(text)
        if at_bottom:  
            scrollbar.setValue(scrollbar.maximum())

class TaskList(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        label = QLabel("Task list")
        label.setStyleSheet(f"font-size: 25px; color: #456; border: 2px solid {BORDER};")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        label = QLabel("Task Inspector")
        label.setStyleSheet(f"font-size: 25px; color: #456;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        self.task_list = QWidget()
        self.task_list_layout = QVBoxLayout(self.task_list)
        self.task_list_layout.setContentsMargins(4, 0, 4, 0)
        self.task_list_layout.setSpacing(4)

        main_layout.addWidget(label, 1)
        main_layout.addWidget(self.task_list, 10)
        main_layout.addStretch()


    def update_tasks(self, tasks: dict[str, Task]):
        while self.task_list_layout.count():
            item = self.task_list_layout.takeAt(0) # Take from index 0 repeatedly
            if item.widget():
                widget = item.widget()
                widget.setParent(None) 
                widget.deleteLater()  
            del item

        for task in tasks.values():
            self.task_list_layout.addWidget(TaskViewObject(task))

        self.task_list_layout.addStretch(1)

    def change_task_object_pos(self, pos):
        # find closest two widgets:
        print(pos)


class TaskInspector(QWidget):

    def __init__(self) -> None:
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(f"border: 2px solid {BORDER}; background-color: red;")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        label = QLabel("Task Inspector")
        label.setStyleSheet(f"font-size: 25px; color: #456;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        self.task_view = QWidget()
        self.task_view.setStyleSheet("background-color: green;")


        self.module_view = QWidget()
        self.module_view.setStyleSheet("background-color: yellow;")

        main_layout.addWidget(label, 1)
        main_layout.addWidget(self.task_view, 5)
        main_layout.addWidget(self.module_view, 5)
        main_layout.addStretch()

class TaskViewer(QWidget):

    def __init__(self) -> None:
        super().__init__()

        self.client = ServerClient()
        self.client.websocket_connected_signal.connect(self.show_connection_state)
        self.client.websocket_message_received_signal.connect(self.websocket_msg)

        self.tasks: dict[str, Task] = {}
        self._get_tasks()


        self.init_ui()
        self.show_connection_state(False)


    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.container = QWidget()
        self.container_layout = QHBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(0)
        
        self.task_list = TaskList()
        # add_task_button = QPushButton("Add task")
        # add_task_button.setStyleSheet(get_push_button_style())
        # task_list_layout.addWidget(add_task_button)


        self.task_inspector = TaskInspector()

        # Server-connection visualization:
        self.blur_effect_list = QGraphicsBlurEffect()
        self.blur_effect_inspector = QGraphicsBlurEffect()
        self.task_inspector.setGraphicsEffect(self.blur_effect_inspector)
        self.task_list.setGraphicsEffect(self.blur_effect_list)

        self.blur_effect_list.setEnabled(False)
        self.blur_effect_inspector.setEnabled(False)
        self.overlay = None

        self.container_layout.addWidget(self.task_list, 4)
        self.container_layout.addWidget(self.task_inspector, 1)
        main_layout.addWidget(self.container, 8)

        self.server_container = ServerViewer(self.client)
        main_layout.addWidget(self.server_container, 2)

        main_layout.addStretch()

    def show_overlay(self):
        self.overlay = ServerConnectOverlay(self.client, self.container)
        self.overlay.move(0, 0)
        self.overlay.resize_event()
        self.blur_effect_list.setEnabled(True)
        self.blur_effect_inspector.setEnabled(True)
        self.overlay.show()

    def hide_overlay(self):
        if self.overlay:
            self.overlay.close()
            self.overlay.deleteLater()
            self.overlay = None
            self.blur_effect_list.setEnabled(False)
            self.blur_effect_inspector.setEnabled(False)

    @Slot(bool)
    def show_connection_state(self, connected: bool):
        if connected and self.overlay is not None:
            self.hide_overlay()
            self._get_tasks()
            self.task_list.update_tasks(self.tasks)
        elif not connected and self.overlay is None:
            self.show_overlay()

    def _get_tasks(self):
        self.tasks = {}
        tasks = self.client.get_all_tasks_from_server()
        if tasks is not None:
            for task in tasks:
                self.tasks[task.task_id] = task

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.overlay:
            self.overlay.resize_event()

    @Slot(dict)
    def websocket_msg(self, msg: dict):
        if msg["type"] == "task_added":
            self._get_tasks()
            self.task_list.update_tasks(self.tasks)

