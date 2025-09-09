from PySide6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QSizePolicy, QTextEdit, QVBoxLayout, QWidget,
                               QGraphicsBlurEffect, QFrame)
from PySide6.QtCore import Qt, Signal, Slot
from pydantic import main

from .server_client import ServerClient, ServerConnectOverlay, ServerViewer
from .task_view_object import TaskViewObject
from .task_inspector import TaskInspector
from .task_list import TaskList

from ..helper import LoadingSpinner, LabelEntry, SelectAllLineEdit
from ..styles import BORDER, get_delete_button_style, get_main_window_style, get_push_button_style, get_toolbar_style, BG1

from Server.Backend.types import Module, Task, TaskTemplate




class TaskViewer(QWidget):

    task_changed_signal = Signal(Task)
    task_list_changed_signal = Signal(dict)
    module_changed_signal = Signal(Module)

    def __init__(self) -> None:
        super().__init__()

        self.client = ServerClient()
        self.client.websocket_connected_signal.connect(self.websocket_connection_changed)
        self.client.websocket_message_received_signal.connect(self.websocket_msg)

        self.tasks: dict[str, Task] = {}
        self.selected_task = None
        self._get_tasks()


        self.init_ui()
        self.websocket_connection_changed(False)


    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.container = QWidget()
        self.container_layout = QHBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(0)
        
        self.task_list = TaskList(self.client)
        self.task_list_changed_signal.connect(self.task_list.update_tasks)
        self.task_changed_signal.connect(self.task_list.update_task)


        self.task_inspector = TaskInspector(self.client)
        self.task_list.task_selected_signal.connect(self.task_inspector.update_task)
        # self.task_changed_signal.connect(self.task_list.

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

        self.server_viewer = ServerViewer(self.client)
        main_layout.addWidget(self.server_viewer, 2)

        main_layout.addStretch()

    def show_overlay(self):
        self.overlay = ServerConnectOverlay(self.client, self.container)
        self.server_viewer.loading_signal.connect(self.overlay.loading)
        self.overlay.move(0, 0)
        self.overlay.resize_event()
        self.blur_effect_list.setEnabled(True)
        self.blur_effect_inspector.setEnabled(True)
        self.overlay.show()

    def hide_overlay(self):
        if self.overlay:
            self.overlay.loading(False)
            self.server_viewer.loading_signal.disconnect(self.overlay.loading)
            self.overlay.close()
            self.overlay.deleteLater()
            self.overlay = None
            self.blur_effect_list.setEnabled(False)
            self.blur_effect_inspector.setEnabled(False)

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


    def update_tasks(self):
        ...

    @Slot(bool)
    def websocket_connection_changed(self, connected: bool):
        if connected:
            self._get_tasks()
            # self.task_list.update_tasks(self.tasks)
            self.task_list_changed_signal.emit(self.tasks)
            if self.overlay is not None:
                self.hide_overlay()
        else:
            if self.overlay is None:
                self.show_overlay()
            self.tasks = {}
            self.task_list_changed_signal.emit(self.tasks)
            self.task_list.task_clicked(None)

    @Slot(dict)
    def websocket_msg(self, msg: dict):
        if msg["type"] == "task_added":
            self._get_tasks()
            self.task_list_changed_signal.emit(self.tasks)
        if msg["type"] == "task_property_changed":
            try:
                task_id = msg["task_id"]
                new_task = self.client.get_task_from_server(task_id)
                if new_task is not None:
                    self.tasks[task_id] = new_task
                self.task_changed_signal.emit(task_id)
            except:
                pass

