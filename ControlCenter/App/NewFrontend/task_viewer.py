from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QSpacerItem, QPushButton, QScrollArea
)
from PySide6.QtCore import Qt, Signal, Slot
from typing import override

from App.NewBackend.task import Task, TaskState
from App.NewBackend.module import Module, ModuleState
from .settings_vis import SettingVis
from .task_window import TaskWindow
from .styles import *
from .settings_editor import SettingsEditor
from .metadata_editor import MetaDataEditor

class ClickableLabel(QWidget):
    clicked_signal = Signal(Task)

    def __init__(self, text: str = "", bound_object = None):
        super().__init__()
        self.text = text
        self.is_clicked = False
        self.object = bound_object
        self.init_ui()

    def init_ui(self):
        self.setFixedHeight(20)
        layout = QHBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 6, 0)
        self.label = QLabel(self.text)
        self.label.setStyleSheet(get_task_label_style())
        layout.addWidget(self.label, 1)
        layout.addStretch()

    @override
    def mousePressEvent(self, event):
        self.clicked_signal.emit(self.object)

    def clicked(self):
        if self.is_clicked:
            self.is_clicked = False
            self.label.setStyleSheet(get_task_label_style())
        else:
            self.is_clicked = True
            self.label.setStyleSheet(get_task_label_style_clicked())


class TaskInfo(QFrame):
    selected_module_changed_signal = Signal(Module)

    def __init__(self, task: Task = None):
        super().__init__()
        self.task = task
        self.module_labels = {}
        self.clicked_module = None
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(f"border: 2px solid {BORDER};")
        task_info_layout = QVBoxLayout(self)
        task_info_layout.setContentsMargins(0, 0, 0, 0)

        self.name_label = QLabel("No task selected")
        self.name_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #555; padding: 2px; border: none;")
        self.status_label = QLabel("Status: ")
        self.status_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #555; padding: 2px; border: none;")
        task_info_layout.addWidget(self.name_label)
        task_info_layout.addWidget(self.status_label)

        meta_data_label = QLabel("Meta Data: ")
        meta_data_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #555; padding: 2px; border: none;")
        task_info_layout.addWidget(meta_data_label)
        self.meta_data_scroll_area = QScrollArea()
        self.meta_data_scroll_area_layout = QVBoxLayout()
        self.meta_data_scroll_area.setWidgetResizable(True)
        self.meta_data_scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn
        )

        self.meta_data_scroll_area.setStyleSheet(f"border: none; background-color: {BG1};")
        self.meta_data_scroll_area.setLayout(self.meta_data_scroll_area_layout)
        task_info_layout.addWidget(self.meta_data_scroll_area, 2)

        self.edit_meta_data_button = QPushButton("Edit Metadata")
        self.edit_meta_data_button.setStyleSheet(get_push_button_style())
        self.edit_meta_data_button.setFixedHeight(40)
        self.edit_meta_data_button.setDisabled(True)
        self.edit_meta_data_button.clicked.connect(self.edit_meta_data)
        task_info_layout.addWidget(self.edit_meta_data_button)

        module_label = QLabel("Modules: ")
        module_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #555; padding: 2px; border: none;")
        task_info_layout.addWidget(module_label)
        self.module_scroll_area = QScrollArea()
        self.module_scroll_area_layout = QVBoxLayout()
        self.module_scroll_area.setWidgetResizable(True)
        self.module_scroll_area.setVerticalScrollBarPolicy(
            # Qt.ScrollBarPolicy.ScrollBarAsNeeded
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn
        )

        self.module_scroll_area.setStyleSheet(f"border: none; background-color: {BG1};")
        self.module_scroll_area.setLayout(self.module_scroll_area_layout)
        task_info_layout.addWidget(self.module_scroll_area, 3)

        task_info_layout.addStretch()

        self.add_module_button = QPushButton("Add Module")
        self.add_module_button.setStyleSheet(get_push_button_style())
        self.add_module_button.setFixedHeight(40)
        self.add_module_button.setDisabled(True)
        task_info_layout.addWidget(self.add_module_button)

        self.delete_task_button = QPushButton("Delete Task")
        self.delete_task_button.setStyleSheet(get_delete_button_style())
        self.delete_task_button.setFixedHeight(40)
        self.delete_task_button.setDisabled(True)
        self.delete_task_button.clicked.connect(self.delete_task)
        task_info_layout.addWidget(self.delete_task_button)


    def delete_task(self):
        if self.task is not None:
            self.task.delete()

    @Slot(Task)
    def update_view(self, new_task: Task):
        if self.task is not None:
            self.task.task_state_changed_signal.disconnect(self.update_state)
            self.task.task_modules_changed_signal.disconnect(self.module_list_changed)
            self.task.task_meta_data_changed_signal.disconnect(self.update_meta_data)

        self.task = new_task
        if self.task is None:
            self.name_label.setText("No task selected")
            self.name_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #555; padding: 2px; border: none;")
            self.status_label.setText("Status: ")
            self.status_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #555; padding: 2px; border: none;")
            self.edit_meta_data_button.setDisabled(True)
            self.add_module_button.setDisabled(True)
            self.delete_task_button.setDisabled(True)
        else:
            self.name_label.setText(self.task.name)
            self.name_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #0056b3; padding: 2px; border: none;")
            self.status_label.setText(f"Status: {self.task.get_state().name}")
            self.status_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #333; padding: 2px; border: none;")
            self.edit_meta_data_button.setDisabled(False)
            self.add_module_button.setDisabled(False)
            self.delete_task_button.setDisabled(False)

        self.update_module_list()
        self.update_meta_data()

        if self.task is not None:
            self.task.task_state_changed_signal.connect(self.update_state)
            self.task.task_modules_changed_signal.connect(self.module_list_changed)
            self.task.task_meta_data_changed_signal.connect(self.update_meta_data)

    @Slot(TaskState)
    def update_state(self, _: TaskState):
        self.status_label.setText(f"Status: {self.task.get_state().name}")

    @Slot()
    def update_meta_data(self):
        while self.meta_data_scroll_area_layout.count():
            item = self.meta_data_scroll_area_layout.takeAt(0) # Take from index 0 repeatedly
            if item.widget():
                widget = item.widget()
                widget.setParent(None) 
                widget.deleteLater()  
            del item

        if self.task is None:
            return

        for name in self.task._meta_data.keys():
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            name_label = QLabel(name)
            name_label.setStyleSheet("font-size: 12px;")
            value_label = QLabel(self.task._meta_data[name])
            value_label.setStyleSheet("font-size: 12px;")
            value_label.setWordWrap(True)
            row.addWidget(name_label)
            row.addWidget(value_label)
            self.meta_data_scroll_area_layout.addLayout(row)
            spacer = QWidget()
            spacer.setStyleSheet(f"background-color: {BORDER};")
            spacer.setFixedHeight(4)
            self.meta_data_scroll_area_layout.addWidget(spacer)

        self.meta_data_scroll_area_layout.addStretch()

    def update_module_list(self):
        while self.module_scroll_area_layout.count():
            item = self.module_scroll_area_layout.takeAt(0) # Take from index 0 repeatedly
            if item.widget():
                widget = item.widget()
                widget.setParent(None) 
                widget.deleteLater()  
            del item

        self.module_labels = {}
        # self.clicked_module = None
        self.module_clicked(None)
        if self.task is None:
            return

        for m in self.task._modules:
            label = ClickableLabel(m._name, m)
            label.setStyleSheet("font-size: 12px;")
            self.module_scroll_area_layout.addWidget(label)
            self.module_labels[m] = label
            label.clicked_signal.connect(self.module_clicked)
        self.module_scroll_area_layout.addStretch()

    @Slot(Module)
    def module_clicked(self, module: Module | None):
        if module is None:
            self.clicked_module = None
        elif self.clicked_module is None:
            self.module_labels[module].clicked()
            self.clicked_module = module
        elif self.clicked_module == module:
            self.module_labels[module].clicked()
            self.clicked_module = None
        elif self.clicked_module is not None:
            self.module_labels[self.clicked_module].clicked()
            self.module_labels[module].clicked()
            self.clicked_module = module
        self.selected_module_changed_signal.emit(self.clicked_module)

    def remove_module(self):
        self.module_labels[self.clicked_module].setParent(None)
        self.module_labels[self.clicked_module].deleteLater()
        self.task.remove_module(self.clicked_module)
        self.clicked_module = None
        self.selected_module_changed_signal.emit(self.clicked_module)

    @Slot()
    def module_list_changed(self):
        self.update_module_list()

    def edit_meta_data(self):
        editor = MetaDataEditor()
        editor.exec()


class ModuleInfo(QFrame):
    def __init__(self, task_info: TaskInfo, module: Module = None):
        super().__init__()
        self.module = module
        self.task_info = task_info
        self.task_info.selected_module_changed_signal.connect(self.update_view)
        self.setting_labels = {}
        self.clicked_setting = None

        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(f"border: 2px solid {BORDER}")
        module_info_layout = QVBoxLayout(self)
        module_info_layout.setContentsMargins(2, 0, 2, 4)
        module_info_layout.setSpacing(4)

        self.name_label = QLabel("No module selected")
        self.name_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #555; padding: 2px; border: none;")
        self.status_label = QLabel("Status: ")
        self.status_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #555; padding: 2px; border: none;")
        module_info_layout.addWidget(self.name_label)
        module_info_layout.addWidget(self.status_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn
        )
        self.scroll_area.setStyleSheet(f"border: none; background-color: {BG1};")
        self.scroll_area_layout = QVBoxLayout()
        # self.scroll_area_layout.setContentsMargins(0, 2, 0, 0)
        self.scroll_area_layout.setSpacing(4)

        self.scroll_area.setLayout(self.scroll_area_layout)
        module_info_layout.addWidget(self.scroll_area, 1)
        module_info_layout.addStretch()

        self.edit_settings_button = QPushButton("Edit Settings")
        self.edit_settings_button.setFixedHeight(40)
        self.edit_settings_button.setStyleSheet(get_push_button_style())
        self.edit_settings_button.setDisabled(True)
        self.edit_settings_button.clicked.connect(self.settings_editor)

        module_info_layout.addWidget(self.edit_settings_button)

        self.remove_module_button = QPushButton("Remove Module")
        self.remove_module_button.clicked.connect(self.task_info.remove_module)
        self.remove_module_button.setStyleSheet(get_delete_button_style())
        self.remove_module_button.setFixedHeight(40)
        self.remove_module_button.setDisabled(True)
        module_info_layout.addWidget(self.remove_module_button)


        b1 = QPushButton("Idle")
        b1.clicked.connect(lambda: self.module.set_state(ModuleState.NotExecuted))
        b2 = QPushButton("Finished")
        b2.clicked.connect(lambda: self.module.set_state(ModuleState.Finished))
        module_info_layout.addWidget(b1)
        module_info_layout.addWidget(b2)


    @Slot(Module)
    def update_view(self, new_module: Module):
        if self.module is not None:
            self.module.module_state_changed_signal.disconnect(self.update_state)

        self.module = new_module
        if self.module is None:
            self.name_label.setText("No module selected")
            self.name_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #555; padding: 2px; border: none;")
            self.status_label.setText("Status: ")
            self.status_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #555; padding: 2px; border: none;")
            self.edit_settings_button.setDisabled(True)
            self.remove_module_button.setDisabled(True)
        else:
            self.name_label.setText(self.module._name)
            self.name_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #0056b3; padding: 2px; border: none;")
            self.status_label.setText(f"Status: {self.module.get_state().name}")
            self.status_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #333; padding: 2px; border: none;")
            self.remove_module_button.setDisabled(False)

            if self.module.get_state() == ModuleState.Running or self.module.get_state() == ModuleState.Finished:
                self.edit_settings_button.setDisabled(True)
            else:
                self.edit_settings_button.setDisabled(False)

        self.update_setting_list()

        if self.module is not None:
            self.module.module_state_changed_signal.connect(self.update_state)


    @Slot(ModuleState)
    def update_state(self, new_state: ModuleState):
        self.status_label.setText(f"Status: {self.module.get_state().name}")

        # activate edit button
        if new_state == ModuleState.Running or new_state == ModuleState.Finished:
            self.edit_settings_button.setDisabled(True)
        else:
            self.edit_settings_button.setDisabled(False)

    def update_setting_list(self):
        while self.scroll_area_layout.count():
            item = self.scroll_area_layout.takeAt(0) # Take from index 0 repeatedly
            if item.widget():
                widget = item.widget()
                widget.setParent(None) 
                widget.deleteLater()  
            del item

        self.setting_labels = {}
        if self.module is None:
            return

        # self.scroll_area_layout.addSpacerItem(QSpacerItem(20, 20))
        for s in self.module._external_settings:
            setting = SettingVis(s)
            self.scroll_area_layout.addWidget(setting)
            self.setting_labels[s] = setting
        self.scroll_area_layout.addStretch()

    @Slot()
    def settings_editor(self):
        editor = SettingsEditor(self.module)
        editor.exec()


class TaskViewer(QWidget):
    def __init__(self, task_window: TaskWindow, task: Task = None):
        super().__init__()
        self.task = task
        self.task_window = task_window
        self.task_window.selected_task_changed_signal.connect(self.update_view)

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setStyleSheet(f"background-color: {BG2};")

        # task info
        self.task_info = TaskInfo(self.task)
        self.task_window.selected_task_changed_signal.connect(self.task_info.update_view)
        main_layout.addWidget(self.task_info, 3)

        # module info
        module_info = ModuleInfo(self.task_info)
        main_layout.addWidget(module_info, 2)

        self.start_task_button = QPushButton("Start Task")
        self.start_task_button.setStyleSheet(get_start_button_style())
        self.start_task_button.setFixedHeight(40)
        self.start_task_button.setDisabled(True)

        main_layout.addWidget(self.start_task_button)

        main_layout.addStretch()

    @Slot(Task)
    def update_view(self, new_task: Task):
        if new_task is None:
            self.start_task_button.setDisabled(True)
        else:
            self.start_task_button.setDisabled(False)
