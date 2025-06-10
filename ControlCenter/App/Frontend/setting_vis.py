from PySide6.QtWidgets import (
    QHBoxLayout,
    QWidget,
    QFileDialog,
    QPushButton,
    QCheckBox,
    QLabel,
    QComboBox,
    QLineEdit,
    QFrame,
)
from PySide6.QtCore import Qt, QLocale
from PySide6.QtGui import QIntValidator, QDoubleValidator
from App.Backend.settings import Setting, Option
from .helper import TreeNode
import os


class IntInput(QLineEdit):
    def __init__(self, value: int, setting: Setting, parent=None):
        super().__init__(parent)
        self.setValidator(QIntValidator())
        self.setting = setting
        self.textChanged.connect(self.update_setting)
        self.setText(str(value))

    def update_setting(self):
        if self.validate():
            self.setting.value = int(self.text())

    def validate(self):
        if self.hasAcceptableInput():
            self.setStyleSheet("background-color: #e0ffe0")  # light green
            return True
        else:
            self.setStyleSheet("background-color: #ffe0e0")  # light red
            return False

    def value(self):
        return int(self.text()) if self.hasAcceptableInput() else None

    def set_editable(self, editable: bool):
        self.setEnabled(editable)


class FloatInput(QLineEdit):
    def __init__(self, value: float, setting: Setting, parent=None):
        super().__init__(parent)
        self.setting = setting
        validator = QDoubleValidator()
        validator.setLocale(QLocale("C"))
        self.setValidator(validator)
        self.textChanged.connect(self.update_setting)
        self.setText(str(value))

    def update_setting(self):
        if self.validate():
            self.setting.value = float(self.text())

    def validate(self):
        if self.hasAcceptableInput():
            self.setStyleSheet("background-color: #e0ffe0")
            return True
        else:
            self.setStyleSheet("background-color: #ffe0e0")
            return False

    def value(self):
        return float(self.text()) if self.hasAcceptableInput() else None

    def set_editable(self, editable: bool):
        self.setEnabled(editable)


class PathInput(QFrame):
    def __init__(
        self,
        value: str,
        setting: Setting,
        select_files=True,
        parent=None,
        check: bool = True,
    ):
        super().__init__(parent)
        self.select_files = select_files
        self.setting = setting
        self.check = check

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        # self.setFixedHeight(30)
        self.edit = QLineEdit()
        self.button = QPushButton("📁")
        self.button.setFixedWidth(30)
        self.button.clicked.connect(self.browse)
        self.edit.textChanged.connect(self.update_setting)
        self.edit.setText(value)

        layout.addWidget(self.edit)
        layout.addWidget(self.button)

    def update_setting(self):
        if not self.check or self.validate():
            self.setting.value = self.edit.text()

    def browse(self):
        if self.select_files:
            path, _ = QFileDialog.getOpenFileName(self, "Select File")
        else:
            path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if path:
            self.edit.setText(path)

    def validate(self):
        path = self.edit.text()
        if os.path.exists(path):
            self.edit.setStyleSheet("background-color: #e0ffe0")
            return True
        else:
            self.edit.setStyleSheet("background-color: #ffe0e0")
            return False

    def value(self):
        path = self.edit.text()
        return path if os.path.exists(path) else None

    def set_editable(self, editable: bool):
        self.setEnabled(editable)


class StringInput(QLineEdit):
    def __init__(self, value: str, setting: Setting, parent=None):
        super().__init__(parent)
        self.setText(value)
        self.setting = setting
        self.textChanged.connect(self.update_setting)

    def update_setting(self):
        self.setting.value = self.text()

    def value(self) -> str:
        return self.text()

    def is_valid(self) -> bool:
        return bool(self.text().strip())

    def set_editable(self, editable: bool):
        self.setEnabled(editable)


class BoolInput(QCheckBox):
    def __init__(self, value: bool, setting: Setting, parent=None):
        super().__init__(parent)
        self.setChecked(value)
        self.setting = setting
        self.checkStateChanged.connect(self.update_setting)

    def update_setting(self):
        self.setting.value = self.isChecked()

    def value(self) -> bool:
        return self.isChecked()

    def is_valid(self) -> bool:
        return True  # A bool is always valid

    def set_editable(self, editable: bool):
        self.setEnabled(editable)


class OptionInput(QComboBox):
    def __init__(self, value: str, setting: Setting, options: list[str], parent=None):
        super().__init__(parent)
        self.addItems(options)
        self.setCurrentText(value)
        self.currentTextChanged.connect(self.update_setting)
        self.setting = setting

    def update_setting(self):
        self.setting.value = self.currentText()

    def value(self) -> str:
        return self.currentText()

    def is_valid(self) -> bool:
        return self.currentIndex() >= 0

    def set_editable(self, editable: bool):
        self.setEnabled(editable)


class SettingObject(TreeNode):
    def __init__(self, setting: Setting):
        super().__init__()
        self.setting = setting
        self.init_ui()

    def init_ui(self):
        frame = QFrame()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        label = QLabel(self.setting.name + ": " + self.setting.type_name)
        layout.addWidget(label, 2)

        if self.setting.type_name == "bool":
            self.input = BoolInput(self.setting.value, self.setting)
        elif self.setting.type_name == "int":
            self.input = IntInput(self.setting.value, self.setting)
        elif self.setting.type_name == "double":
            self.input = FloatInput(self.setting.value, self.setting)
        elif self.setting.type_name == "string":
            self.input = StringInput(self.setting.value, self.setting)
        elif self.setting.type_name == "option":
            self.input = OptionInput(
                self.setting.value, self.setting, self.setting.type.options
            )
        elif self.setting.type_name == "file":
            self.input = PathInput(
                self.setting.value, self.setting, True, check=self.setting.check
            )
        elif self.setting.type_name == "folder":
            self.input = PathInput(
                self.setting.value, self.setting, False, check=self.setting.check
            )
        else:
            self.input = QLineEdit()

        self.input.setFixedHeight(18)
        layout.addWidget(self.input, 1)
        layout.addStretch()
        self.add_object([frame])
        # self.setText(1, str(self.setting.value))
