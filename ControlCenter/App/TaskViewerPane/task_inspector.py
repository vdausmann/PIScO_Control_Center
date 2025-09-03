from PySide6.QtWidgets import (QLabel, QPushButton, QScrollArea, QSizePolicy, QVBoxLayout, QWidget)
from PySide6.QtCore import Qt, Slot

from ..styles import BORDER, get_push_button_style
from ..helper import LabelEntry, SelectAllLineEdit

from Server.Backend.types import Task

class TaskInspector(QWidget):

    def __init__(self) -> None:
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(f"border: 2px solid {BORDER};")
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
        meta_data_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        self.meta_data_layout = QVBoxLayout()
        self.meta_data_layout.setContentsMargins(2, 2, 2, 2)
        meta_data_area.setLayout(self.meta_data_layout)

        self.task_view_layout.addWidget(meta_data_area, 1)

        edit_metadata_button = QPushButton("Edit metadata")
        edit_metadata_button.setStyleSheet(get_push_button_style())
        self.task_view_layout.addWidget(edit_metadata_button)

        ##########################
        ## Module list
        ##########################
        modules_label = QLabel("Modules:")
        modules_label.setStyleSheet(f"font-size: 15px; color: #456; border: none;")
        self.task_view_layout.addWidget(modules_label)
        modules_area = QScrollArea()
        modules_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        self.modules_layout = QVBoxLayout()
        self.modules_layout.setContentsMargins(2, 2, 2, 2)
        modules_area.setLayout(self.modules_layout)

        self.task_view_layout.addWidget(modules_area, 1)

        edit_modules_button = QPushButton("Edit modules")
        edit_modules_button.setStyleSheet(get_push_button_style())
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
    def update_task(self, selected_task: Task | None):
        if selected_task is None:
            self.task_label.setText("No task selected")
            self.task_id_label.entry.setText("")
            self.update_metadata_area({})
            self.update_modules_area([])
        else:
            self.task_label.setText(selected_task.name)
            self.task_id_label.entry.setText(f"{selected_task.task_id}")
            self.update_metadata_area(selected_task.meta_data)
            self.update_modules_area(selected_task.modules)

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0) # Take from index 0 repeatedly
            if item.widget():
                widget = item.widget()
                widget.setParent(None) 
                widget.deleteLater()  
            del item

    def update_metadata_area(self, meta_data: dict):
        self.clear_layout(self.meta_data_layout)
        for key in meta_data.keys():
            l = QLabel(f"{key}: {meta_data[key]}")
            l.setStyleSheet(f"font-size: 12px; color: #456; border: none;")
            self.meta_data_layout.addWidget(l)
        self.meta_data_layout.addStretch()

    def update_modules_area(self, modules: list[str]):
        self.clear_layout(self.modules_layout)
        print(modules)
        for module_id in modules:
            l = SelectAllLineEdit(module_id)
            l.setReadOnly(True)
            l.setStyleSheet(f"font-size: 12px; color: #456; border: none; background-color: transparent;")
            self.modules_layout.addWidget(l)
        self.modules_layout.addStretch()

