from PySide6.QtWidgets import (QLabel, QPushButton, QScrollArea, QSizePolicy, QVBoxLayout, QWidget)
from PySide6.QtCore import Qt, Slot

from .server_client import ServerClient
from .meta_data_editor import EditMetaDataDialog

from ..helper import LabelEntry, SelectAllLineEdit, clear_layout

from Server.Backend.types import Task

class TaskInspector(QWidget):

    def __init__(self, client: ServerClient) -> None:
        super().__init__()
        self.client = client
        self.inspected_task_id: str | None = None
        self.inspected_task: Task | None = None
        self.init_ui()

    def init_ui(self):
        # self.setStyleSheet(f"border: 2px solid {BORDER};")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        label = QLabel("Task Inspector")
        label.setStyleSheet(f"font-size: 25px; color: #456;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        main_layout.addWidget(label, 1)

        self.task_view = QWidget()
        self.task_view_layout = QVBoxLayout(self.task_view)
        self.task_view_layout.setContentsMargins(4, 4, 4, 4)
        self.task_view_layout.setSpacing(2)
        self.task_label = QLabel("No task selected")
        self.task_label.setStyleSheet(f"font-size: 20px; color: #456; border: none;")
        self.task_view_layout.addWidget(self.task_label)

        ##########################
        ## Task info
        ##########################
        self.task_id_label = LabelEntry(label_ratio=1, entry_ratio=6, entry_class=SelectAllLineEdit)
        self.task_id_label.entry.setReadOnly(True)
        self.task_id_label.label.setStyleSheet(f"font-size: 12px; color: #456; border: none;")
        self.task_id_label.entry.setStyleSheet(f"font-size: 12px; color: #456; background-color: transparent; border: none;")
        self.task_id_label.label.setText("    ID: ")
        self.task_id_label.entry.setText("")
        self.task_view_layout.addWidget(self.task_id_label)

        ##########################
        ## Meta data
        ##########################
        meta_data_label = QLabel("Meta data:")
        meta_data_label.setStyleSheet(f"font-size: 15px; color: #456; border: none;")
        self.task_view_layout.addWidget(meta_data_label)
        meta_data_area = QScrollArea()
        meta_data_area.setWidgetResizable(True)
        meta_data_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        meta_data_container = QWidget()
        self.meta_data_layout = QVBoxLayout(meta_data_container)
        self.meta_data_layout.setContentsMargins(2, 2, 2, 2)
        meta_data_area.setWidget(meta_data_container)

        self.task_view_layout.addWidget(meta_data_area, 1)

        edit_metadata_button = QPushButton("Edit metadata")
        edit_metadata_button.clicked.connect(self.edit_meta_data)
        self.task_view_layout.addWidget(edit_metadata_button)

        ##########################
        ## Module list
        ##########################
        modules_label = QLabel("Modules:")
        modules_label.setStyleSheet(f"font-size: 15px; color: #456; border: none;")
        self.task_view_layout.addWidget(modules_label)
        modules_area = QScrollArea()
        modules_area.setWidgetResizable(True)
        modules_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        modules_container = QWidget()
        self.modules_layout = QVBoxLayout(modules_container)
        self.modules_layout.setContentsMargins(2, 2, 2, 2)
        modules_area.setWidget(modules_container)

        self.task_view_layout.addWidget(modules_area, 1)

        edit_modules_button = QPushButton("Edit modules")
        self.task_view_layout.addWidget(edit_modules_button)



        self.task_view_layout.addStretch()
        main_layout.addWidget(self.task_view, 5)

        ##########################
        ## Module inspector
        ##########################
        self.module_view = QWidget()
        self.module_view.setStyleSheet("background-color: yellow;")

        main_layout.addWidget(self.module_view, 5)
        main_layout.addStretch()

    @Slot(object)
    def update_task(self, selected_task: str | None):
        self.inspected_task_id = selected_task

        if self.inspected_task_id is None  or not self.inspected_task_id:
            self.inspected_task = None
            self.task_label.setText("No task selected")
            self.task_id_label.entry.setText("")
            self.update_meta_data_area()
            self.update_modules_area()
        else:
            self.inspected_task = self.client.get_task_from_server(self.inspected_task_id)
            if self.inspected_task is None:
                return self.update_task(None)
            
            self.task_label.setText(self.inspected_task.name)
            self.task_id_label.entry.setText(f"{self.inspected_task_id}")
            self.update_meta_data_area()
            self.update_modules_area()

    def update_meta_data_area(self):
        clear_layout(self.meta_data_layout)
        if self.inspected_task is None:
            return
        for key in self.inspected_task.meta_data.keys():
            l = QLabel(f"{key}: {self.inspected_task.meta_data[key]}")
            l.setStyleSheet(f"font-size: 12px; color: #456; border: none;")
            self.meta_data_layout.addWidget(l)
        self.meta_data_layout.addStretch()

    def update_modules_area(self):
        clear_layout(self.modules_layout)
        if self.inspected_task is None:
            return
        for module_id in self.inspected_task.modules:
            l = SelectAllLineEdit(module_id)
            l.setReadOnly(True)
            l.setStyleSheet(f"font-size: 12px; color: #456; border: none; background-color: transparent;")
            self.modules_layout.addWidget(l)
        self.modules_layout.addStretch()

    @Slot()
    def edit_meta_data(self):
        if self.inspected_task is None:
            return
        meta_data = self.inspected_task.meta_data
        dialog = EditMetaDataDialog(meta_data=meta_data)
        dialog.exec()

        for key in dialog.meta_data:
            if not key in self.inspected_task.meta_data or dialog.meta_data[key] != self.inspected_task.meta_data[key]:
                self.client.change_task_property(self.inspected_task.task_id, f"meta_data.{key}", dialog.meta_data[key])

        # self.inspected_task.meta_data = dialog.meta_data
        # self.update_meta_data_area()
