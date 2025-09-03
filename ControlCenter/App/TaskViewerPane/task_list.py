from PySide6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QSizePolicy, QVBoxLayout, QWidget)

from PySide6.QtCore import Qt, Signal, Slot

from ..styles import BORDER
from .server_client import ServerClient
from .task_view_object import TaskViewObject
from Server.Backend.types import Task, TaskTemplate


class AddTaskDialog(QDialog):

    def __init__(self) -> None:
        super().__init__()

        self.task: TaskTemplate | None = None
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(400, 200)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        label = QLabel("Add task")
        label.setStyleSheet("font-size: 25px; color: #456;")
        main_layout.addWidget(label)

        row = QHBoxLayout()
        row.setSpacing(10)
        row.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit()
        row.addWidget(self.name_edit)
        main_layout.addLayout(row)

        main_layout.addStretch()

        button_row = QHBoxLayout()
        accept_button = QPushButton("Ok")
        accept_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_row.addWidget(accept_button)
        button_row.addWidget(cancel_button)
        main_layout.addLayout(button_row)

    def accept(self) -> None:
        print("Accepted")

        try:
            self.task = TaskTemplate(
                    name=self.name_edit.text(),
                    meta_data={},
                    modules=[]
                    )
        except:
            self.task = None

        return super().accept()

    def get_task(self):
        return self.task

class TaskList(QWidget):
    task_selected_signal = Signal(object) # emits Task or None

    def __init__(self, client: ServerClient) -> None:
        super().__init__()

        self.selected_task: str | None = None
        self.task_objects: dict[str, TaskViewObject] = {}
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
            task_object = TaskViewObject(task)
            task_object.clicked_signal.connect(self.task_clicked)
            self.task_objects[task.task_id] = task_object
            self.task_list_layout.addWidget(task_object)

        self.add_task_button = QPushButton("Add task")
        self.add_task_button.clicked.connect(self.add_task)
        self.task_list_layout.addWidget(self.add_task_button)
        self.task_list_layout.addStretch(1)

    @Slot(str)
    def task_clicked(self, task_id: str):
        # unselect current task:
        if self.selected_task:
            self.task_objects[self.selected_task].select(False)

        # set new selected task
        if task_id == self.selected_task:
            self.selected_task = None
        else:
            self.selected_task = task_id

        # select current task:
        if self.selected_task:
            self.task_objects[self.selected_task].select(True)
            self.task_selected_signal.emit(self.task_objects[self.selected_task].task)
        else:
            self.task_selected_signal.emit(None)

    def change_task_object_pos(self, pos):
        # find closest two widgets:
        print(pos)

    def add_task(self):
        dialog = AddTaskDialog()
        dialog.exec()
        task = dialog.get_task()
        if task is not None:
            self.client.add_task_to_server(task)
            print(task)


