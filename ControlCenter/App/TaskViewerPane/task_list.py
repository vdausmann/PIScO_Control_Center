from PySide6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea,
                               QSizePolicy, QVBoxLayout, QWidget)

from PySide6.QtCore import Qt, Signal, Slot

from .server_client import ServerClient

from ..styles import BORDER
from ..helper import ClickableLabel, StatusLight, clear_layout, replace_widget

from .metadata_view import MetadataView
from .modules_view import ModulesView
from .task_view import TaskView

from Server.Backend.types import ModuleTemplate, Task, TaskTemplate


class TaskWidget(QWidget):
    clicked_signal = Signal()
    double_clicked_signal = Signal()

    def __init__(self, task: Task, parent=None) -> None:
        super().__init__(parent)
        self.task = task

        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(6, 2, 6, 2)
        main_layout.setSpacing(0)

        self.setObjectName("TaskWidget")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.label = QLabel(self.task.name)
        self.label.setStyleSheet(
            "background-color: transparent; border: none; font-size: 16px;"
        )
        main_layout.addWidget(self.label, 1)

        main_layout.addStretch()
        self.status_light = StatusLight(15)
        main_layout.addWidget(self.status_light, alignment=Qt.AlignmentFlag.AlignVCenter)

    def select(self, selected: bool):
        if selected:
            self.setObjectName("TaskWidgetClicked")
            self.style().unpolish(self)
            self.style().polish(self)
        else:
            self.setObjectName("TaskWidget")
            self.style().unpolish(self)
            self.style().polish(self)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked_signal.emit()
        return super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:
        self.double_clicked_signal.emit()
        return super().mouseDoubleClickEvent(event)


class TaskList(QWidget):
    task_selected_signal = Signal(str) # emits task_id or None

    def __init__(self, client: ServerClient) -> None:
        super().__init__()

        self.selected_task: TaskWidget | None = None
        self.task_objects: dict[str, TaskWidget] = {}
        self.client = client

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        label = QLabel("Task list")
        label.setStyleSheet(f"font-size: 25px; color: #456; border: 2px solid {BORDER};")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        label = QLabel("Task List")
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

        self.update_tasks({})


    def update_tasks(self, tasks: dict[str, Task]):
        while self.task_list_layout.count():
            item = self.task_list_layout.takeAt(0) # Take from index 0 repeatedly
            if item.widget():
                widget = item.widget()
                widget.setParent(None) 
                widget.deleteLater()  
            del item

        for task in tasks.values():
            task_object = TaskWidget(task)
            task_object.clicked_signal.connect(self._task_clicked)
            task_object.double_clicked_signal.connect(self.show_task)
            self.task_objects[task.task_id] = task_object
            self.task_list_layout.addWidget(task_object)

        self.add_task_button = QPushButton("Add task")
        self.add_task_button.clicked.connect(self.add_task)
        self.task_list_layout.addWidget(self.add_task_button)
        self.task_list_layout.addStretch(1)

    @Slot(str)
    def update_task(self, task_id: str):
        new_task = self.client.get_task_from_server(task_id)
        if new_task is None:
            # TODO: Remove widget?
            ...
        else:
            new_object = TaskWidget(new_task)
            replace_widget(self.task_list_layout, self.task_objects[task_id], new_object)
            self.task_objects[task_id] = new_object

        print("Updating task", task_id, self.selected_task)
        # send info to task inspector to update the displayed task
        if task_id == self.selected_task:
            self.task_selected_signal.emit(self.selected_task)

    @Slot()
    def _task_clicked(self):
        sender = self.sender()
        if not isinstance(sender, TaskWidget):
            return
        self.task_clicked(sender)

    def task_clicked(self, sender: TaskWidget | None):
        # unselect current task:
        if self.selected_task:
            self.selected_task.select(False)

        # set new selected task
        if sender == self.selected_task:
            self.selected_task = None
        else:
            self.selected_task = sender

        # select current task:
        if self.selected_task:
            self.selected_task.select(True)

        self.task_selected_signal.emit(self.selected_task)

    def change_task_object_pos(self, pos):
        # find closest two widgets:
        print(pos)

    @Slot()
    def show_task(self):
        sender = self.sender()
        if not isinstance(sender, TaskWidget):
            return
        task = sender.task
        dialog = QDialog(self)
        dialog.setFixedSize(400, 600)
        task_view = TaskView(task, self.client)

        dialog_layout = QVBoxLayout(dialog)
        dialog_layout.addWidget(task_view)

        dialog.exec()


    def add_task(self):
        new_task = TaskTemplate(name="", meta_data={}, modules=[])
        dialog = QDialog(self)
        task_view = TaskView(new_task, self.client)

        dialog_layout = QVBoxLayout(dialog)
        dialog_layout.addWidget(task_view)

        dialog.exec()
        # task = dialog.get_task()
        # if task is not None:
        #     self.client.add_task_to_server(task)
        #     print(task)
