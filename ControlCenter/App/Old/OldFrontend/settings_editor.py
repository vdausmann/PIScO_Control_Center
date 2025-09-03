from PySide6.QtWidgets import (
        QLineEdit, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QSpacerItem,
        QPushButton, QScrollArea, QFormLayout, QDialog
)
from PySide6.QtGui import QIntValidator, QDoubleValidator
from PySide6.QtCore import Qt
from App.NewBackend.setting import Setting
from App.NewBackend.module import Module
from .styles import *

class SettingInput(QWidget):
    def __init__(self, setting: Setting):
        super().__init__()
        self.setting = setting

    def init_ui(self):
        ...

    def get_value(self) -> ...:
        ...

    def update_setting(self):
        new_value = self.get_value()
        self.setting.change_value(new_value)

class ScalarSettingInput(SettingInput):
    def __init__(self, setting: Setting, is_int: bool = False):
        super().__init__(setting)
        self.is_int = is_int
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.input = QLineEdit(str(self.setting._value))
        self.input.setStyleSheet("font-size: 12px;")
        self.input.setFixedSize(150, 20)
        if self.is_int:
            validator = QIntValidator()
        else:
            validator = QDoubleValidator()
            validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.input.setValidator(validator)
        layout.addWidget(self.input)
        layout.addStretch()

    def get_value(self):
        if self.is_int:
            return int(self.input.text())
        return float(self.input.text())


class StringSettingInput(SettingInput):
    def __init__(self, setting: Setting):
        super().__init__(setting)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.input = QLineEdit(str(self.setting._value))
        self.input.setStyleSheet("font-size: 12px;")
        self.input.setFixedSize(150, 20)
        layout.addWidget(self.input)
        layout.addStretch()

    def get_value(self):
        return self.input.text()


class SettingVis(QWidget):
    def __init__(self, setting: Setting):
        super().__init__()
        self.setting = setting
        self.input = None
        self.init_ui()

    def init_ui(self):
        setting_type = self.setting._setting_type
        if setting_type == "str":
            self.input = StringSettingInput(self.setting)
        elif setting_type == "int":
            self.input = ScalarSettingInput(self.setting, True)
        elif setting_type == "float":
            self.input = ScalarSettingInput(self.setting, False)
        elif setting_type == "bool":
            ...
        elif setting_type == "file_path":
            ...
        elif setting_type == "folder_path":
            ...
        elif "option" in setting_type:
            ...
        else:
            raise ValueError("Unknown setting_type: " + setting_type)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(10)
        label = QLabel(self.setting._name)
        label.setFixedSize(100, 40)
        label.setWordWrap(True)
        layout.addWidget(label)
        layout.addWidget(self.input)
        layout.addStretch()


class SettingsEditor(QDialog):
    def __init__(self, module: Module, parent=None):
        super().__init__(parent)
        self.module = module
        self.setWindowTitle("Settings Editor")
        self.setModal(True)
        self.setFixedSize(300, 500)
        self.inputs = {}

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        scroll_area = QScrollArea()

        self.form_layout = QVBoxLayout()
        self.form_layout.setContentsMargins(2, 0, 2, 0) # No extra margins for internal layout
        self.form_layout.setSpacing(0)

        internal_label = QLabel("Internal settings:")
        internal_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #555; padding: 2px; border: none;")
        self.form_layout.addWidget(internal_label)
        for setting in self.module._internal_settings:
            input = SettingVis(setting)
            self.inputs[setting] = input
            self.form_layout.addWidget(input)

        external_label = QLabel("External settings:")
        external_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #555; padding: 2px; border: none;")
        self.form_layout.addWidget(external_label)
        for setting in self.module._external_settings:
            input = SettingVis(setting)
            self.inputs[setting] = input
            self.form_layout.addWidget(input)

        self.form_layout.addStretch()
        # self.name_input = QLineEdit()
        # self.description_input = ScalarSettingInput(self.module._external_settings[0])
        # self.form_layout.addRow("Task Name:", self.name_input)
        # self.form_layout.addRow("Description:", self.description_input)
        # self.inputs["Task Name"] = self.name_input
        # self.inputs["Task Description"] = self.description_input

        scroll_area.setLayout(self.form_layout)

        main_layout.addWidget(scroll_area, 8)

        # button_row = QWidget()
        button_row_layout = QHBoxLayout()
        button_row_layout.setContentsMargins(0, 0, 0, 0)

        accept_button = QPushButton("Ok")
        accept_button.clicked.connect(self._accept)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        button_row_layout.addWidget(accept_button)
        button_row_layout.addWidget(cancel_button)


        main_layout.addLayout(button_row_layout, 1)

    def _accept(self):
        for input in self.inputs.values():
            input.input.update_setting()
        self.accept()
