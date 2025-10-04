from PySide6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea,
                               QSizePolicy, QVBoxLayout, QWidget)

from PySide6.QtCore import Qt, Signal, Slot

from .module_editor import AddModulesDialog

from .server_client import ServerClient
from .task_view_object import TaskViewObject
from .meta_data_editor import EditMetaDataDialog

from ..styles import BORDER
from ..helper import clear_layout, replace_widget

from Server.Backend.types import ModuleTemplate, Task, TaskTemplate


class AddTaskDialog(QDialog):

    def __init__(self, server_client: ServerClient) -> None:
        super().__init__()
        self.server_client = server_client

        self.meta_data: dict[str, str] = {}
        self.modules: list[ModuleTemplate] = []
        self.task: TaskTemplate | None = None
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(400, 500)
        main_layout = QVBoxLayout(self)
        # main_layout.setContentsMargins(0, 0, 0, 0)
        # main_layout.setSpacing(0)

        label = QLabel("Add task")
        label.setStyleSheet("font-size: 25px; color: #456;")
        main_layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)

        row = QHBoxLayout()
        row.setSpacing(10)
        name_label = QLabel("Name:")
        name_label.setStyleSheet(f"font-size: 15px; color: #456; border: none;")
        row.addWidget(name_label)
        self.name_edit = QLineEdit()
        row.addWidget(self.name_edit, 1)
        main_layout.addLayout(row)

        #############################
        ## Metadata:
        #############################
        meta_data_label = QLabel("Meta data:")
        meta_data_label.setStyleSheet(f"font-size: 15px; color: #456; border: none;")
        main_layout.addWidget(meta_data_label)

        meta_data_area = QScrollArea()
        meta_data_area.setWidgetResizable(True)
        meta_data_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        meta_data_container =QWidget()
        self.meta_data_layout = QVBoxLayout(meta_data_container)
        self.meta_data_layout.setContentsMargins(0, 0, 0, 0)
        self.meta_data_layout.setSpacing(2)
        # self.meta_data_layout
        # meta_data_area.setLayout(self.meta_data_layout)
        meta_data_area.setWidget(meta_data_container)
        main_layout.addWidget(meta_data_area, 6)

        meta_data_button = QPushButton("Edit metadata")
        meta_data_button.clicked.connect(self.edit_meta_data)
        main_layout.addWidget(meta_data_button, 1)

        #############################
        ## Modules:
        #############################
        modules_label = QLabel("Modules:")
        modules_label.setStyleSheet(f"font-size: 15px; color: #456; border: none;")
        main_layout.addWidget(modules_label)

        modules_area = QScrollArea()
        modules_area.setWidgetResizable(True)
        modules_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        modules_container = QWidget()
        self.modules_layout = QVBoxLayout(modules_container)
        modules_area.setWidget(modules_container)
        main_layout.addWidget(modules_area, 6)

        modules_button = QPushButton("Add modules")
        modules_button.clicked.connect(self.add_modules)
        main_layout.addWidget(modules_button, 1)

        # main_layout.addStretch()

        button_row = QHBoxLayout()
        accept_button = QPushButton("Ok")
        accept_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_row.addWidget(accept_button)
        button_row.addWidget(cancel_button)
        main_layout.addLayout(button_row)

    def accept(self) -> None:
        try:
            self.task = TaskTemplate(
                    name=self.name_edit.text(),
                    meta_data=self.meta_data,
                    modules=self.modules
                    )
        except:
            self.task = None

        return super().accept()

    def get_task(self):
        return self.task


    def edit_meta_data(self):
        dialog = EditMetaDataDialog(meta_data=self.meta_data)
        dialog.exec()
        self.meta_data = dialog.meta_data

        clear_layout(self.meta_data_layout)
        for key in self.meta_data:
            label = QLabel(f"{key}: {self.meta_data[key]}")
            self.meta_data_layout.addWidget(label, 1)

    def add_modules(self):
        dialog = AddModulesDialog(self.server_client)
        dialog.exec()




class TaskList(QWidget):
    task_selected_signal = Signal(str) # emits task_id or None

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
    def update_task(self, task_id: str):
        new_task = self.client.get_task_from_server(task_id)
        if new_task is None:
            # TODO: Remove widget?
            ...
        else:
            new_object = TaskViewObject(new_task)
            replace_widget(self.task_list_layout, self.task_objects[task_id], new_object)
            self.task_objects[task_id] = new_object

        print("Updating task", task_id, self.selected_task)
        # send info to task inspector to update the displayed task
        if task_id == self.selected_task:
            self.task_selected_signal.emit(self.selected_task)

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
            self.task_selected_signal.emit(self.selected_task)
        else:
            self.task_selected_signal.emit(None)

    def change_task_object_pos(self, pos):
        # find closest two widgets:
        print(pos)

    def add_task(self):
        dialog = AddTaskDialog(self.client)
        dialog.exec()
        task = dialog.get_task()
        if task is not None:
            self.client.add_task_to_server(task)
            print(task)


