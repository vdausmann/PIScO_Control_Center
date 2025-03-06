from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QScrollArea, QLabel, QLineEdit, 
    QComboBox, QFrame, QPushButton, QHBoxLayout, QFileDialog)
from PySide6.QtCore import Qt, QLocale
from PySide6.QtGui import QIntValidator, QDoubleValidator


class SettingBlockFloat(QFrame):
    def __init__(self, name, setting, width, height, default):
        super().__init__()

        self.setting = setting
        self.name = name
        self.block_layout = QVBoxLayout(self)
        self.validator = QDoubleValidator()
        self.validator.setLocale(QLocale("C")) # Forces '.' as the decimal separator
        self.options = [] if len(setting) < 2 else setting[1]
        self.init_ui()
        if default is not None:
            self.set(default)

    def init_ui(self): 
        label = QLabel(self.name + ": Float", alignment=Qt.AlignCenter)
        label.setStyleSheet("color: white;")
        self.block_layout.addWidget(label)

        self.input_field = QLineEdit()
        self.input_field.setStyleSheet("background-color: #333;")
        self.input_field.textChanged.connect(self.validate_input)

        self.block_layout.addWidget(self.input_field)

    def validate_input(self):
        text = self.input_field.text()
        if text == "" or self.is_valid(text):
            self.input_field.setStyleSheet("color: white;")  # Normal text color
        else:
            self.input_field.setStyleSheet("color: red;")  # Invalid input turns red

    def is_valid(self, text):
        """Checks if the given text is a valid integer."""
        state, _, _ = self.validator.validate(text, 0)
        return state == QDoubleValidator.State.Acceptable

    def set(self, value: float):
        self.input_field.setText(str(value))

    def get(self):
        text = self.input_field.text()
        return self.input_field.text() if self.is_valid(text) else "0"


class SettingBlockInt(QFrame):
    def __init__(self, name, setting, width, height, default):
        super().__init__()

        self.setting = setting
        self.name = name
        self.validator = QIntValidator()
        self.block_layout = QVBoxLayout(self)
        self.options = [] if len(setting) < 2 else setting[1]
        self.init_ui()
        if default is not None:
            self.set(default)

    def init_ui(self): 
        label = QLabel(self.name + ": Int", alignment=Qt.AlignCenter)
        label.setStyleSheet("color: white;")
        self.block_layout.addWidget(label)

        self.input_field = QLineEdit()
        self.input_field.setStyleSheet("background-color: #333;")
        self.input_field.textChanged.connect(self.validate_input)

        self.block_layout.addWidget(self.input_field)

    def validate_input(self):
        text = self.input_field.text()
        if text == "" or self.is_valid(text):
            self.input_field.setStyleSheet("color: white;")  # Normal text color
        else:
            self.input_field.setStyleSheet("color: red;")  # Invalid input turns red

    def is_valid(self, text):
        """Checks if the given text is a valid integer."""
        state, _, _ = self.validator.validate(text, 0)
        return state == QIntValidator.State.Acceptable

    def set(self, value: int):
        self.input_field.setText(str(value))

    def get(self):
        text = self.input_field.text()
        return self.input_field.text() if self.is_valid(text) else "0"

class SettingBlockPath(QFrame):
    def __init__(self, name, setting, width, height, default):
        super().__init__()

        self.setting = setting
        self.name = name
        self.block_layout = QVBoxLayout(self)
        self.options = [] if len(setting) < 2 else setting[1]
        self.init_ui()
        if default is not None:
            self.set(default)

    def init_ui(self): 
        label = QLabel(self.name + ": Path", alignment=Qt.AlignCenter)
        label.setStyleSheet("color: white;")
        self.block_layout.addWidget(label)

        container = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.input_field = QLineEdit()
        self.input_field.setStyleSheet("background-color: #333;")
        button = QPushButton("+")
        button.setFixedWidth(30)
        button.clicked.connect(self.select_folder)
        layout.addWidget(self.input_field)
        layout.addWidget(button)

        container.setLayout(layout)
        self.block_layout.addWidget(container)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.input_field.setText(folder)

    def set(self, path):
        """Sets a path programmatically."""
        self.input_field.setText(path)

    def get(self):
        return self.input_field.text()


class SettingBlockOption(QFrame):
    def __init__(self, name, setting, width, height, default):
        super().__init__()

        self.setting = setting
        self.name = name
        self.block_layout = QVBoxLayout(self)
        self.options = [] if len(setting) < 2 else setting[1]
        self.init_ui()
        if default is not None:
            self.set(default)

    def init_ui(self): 
        label = QLabel(self.name + ": Option", alignment=Qt.AlignCenter)
        label.setStyleSheet("color: white;")
        self.block_layout.addWidget(label)

        self.input_field = QComboBox()
        if self.options:
            self.input_field.addItems(self.options)
        self.block_layout.addWidget(self.input_field)

    def set(self, option):
        self.input_field.setCurrentText(option)

    def get(self):
        return self.input_field.currentText()


class SettingBlockString(QFrame):
    def __init__(self, name, setting, width, height, default):
        super().__init__()

        self.setting = setting
        self.name = name
        self.block_layout = QVBoxLayout(self)
        self.options = [] if len(setting) < 2 else setting[1]
        self.init_ui()
        if default is not None:
            self.set(default)

    def init_ui(self): 
        label = QLabel(self.name + ": String", alignment=Qt.AlignCenter)
        label.setStyleSheet("color: white;")
        self.block_layout.addWidget(label)

        self.input_field = QLineEdit()
        self.input_field.setStyleSheet("background-color: #333;")

        self.block_layout.addWidget(self.input_field)

    def get(self):
        return self.input_field.text()

class SettingBlockBool(QFrame):
    def __init__(self, name, setting, width, height, default):
        super().__init__()

        self.setting = setting
        self.name = name
        self.block_layout = QVBoxLayout(self)
        self.options = [] if len(setting) < 2 else setting[1]
        self.init_ui()

        if default is not None:
            self.set(default)

    def init_ui(self): 
        label = QLabel(self.name + ": Bool", alignment=Qt.AlignCenter)
        label.setStyleSheet("color: white;")
        self.block_layout.addWidget(label)

        self.input_field = QPushButton("OFF")
        self.input_field.setCheckable(True)
        self.input_field.clicked.connect(self.toggle_switch)
        self.toggle_switch()
        self.toggle_switch()
        self.block_layout.addWidget(self.input_field)

    def toggle_switch(self):
        if self.input_field.isChecked():
            self.input_field.setText("ON")
            self.input_field.setStyleSheet("border: 1px solid #00cc66; background-color: #00cc66; color: white; border-radius: 5px;")
        else:
            self.input_field.setText("OFF")
            self.input_field.setStyleSheet("border: 1px solid #777777; background-color: #555555; color: white; border-radius: 5px;")

    def set(self, value):
        if value != self.input_field.isChecked():
            self.input_field.setChecked(value)
            self.toggle_switch()

    def get(self):
        return self.input_field.isChecked()

class Settings(QWidget):
    def __init__(self, settings):
        super().__init__()

        self.cell_width = 250  # Fixed cell width
        self.cell_height = 60  # Fixed cell height
        self.columns = 2  # Default number of columns

        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)
        self.setStyleSheet("background-color: #404258; color: #eef4ed;")

        # Scroll Area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        # self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Container widget inside scroll area
        self.scroll_widget = QWidget()
        self.grid_layout = QGridLayout(self.scroll_widget)
        self.grid_layout.setSpacing(10)
        self.scroll_widget.setLayout(self.grid_layout)
        self.scroll_area.setWidget(self.scroll_widget)

        self.main_layout.addWidget(self.scroll_area)

        self.settings = {}

        for key in settings["Fields"].keys():
            if "Defaults" in settings.keys() and key in settings["Defaults"].keys():
                self.add_setting(key, settings["Fields"][key], settings["Defaults"][key])
            else:
                self.add_setting(key, settings["Fields"][key])

        self.update_grid()

    def add_setting(self, name: str, settings, default=None):
        """Add a setting block to the grid."""
        setting_type = settings[0]
        if setting_type == "string":
            setting_block = SettingBlockString(name, settings, self.cell_width, self.cell_height, default)
        elif setting_type == "option":
            setting_block = SettingBlockOption(name, settings, self.cell_width, self.cell_height, default)
        elif setting_type == "path":
            setting_block = SettingBlockPath(name, settings, self.cell_width, self.cell_height, default)
        elif setting_type == "bool":
            setting_block = SettingBlockBool(name, settings, self.cell_width, self.cell_height, default)
        elif setting_type == "int":
            setting_block = SettingBlockInt(name, settings, self.cell_width, self.cell_height, default)
        elif setting_type == "float":
            setting_block = SettingBlockFloat(name, settings, self.cell_width, self.cell_height, default)
        else:
            setting_block = QLabel("Unknown setting type")

        setting_block.setFixedSize(self.cell_width, self.cell_height)
        # setting_block.setStyleSheet("background-color: #333; border: 1px solid #555; border-radius: 5px;")

        self.settings[name] = setting_block
        # self.update_grid()

    def update_grid(self):
        """Rearrange settings based on available space."""
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)

        rows = max(1, len(self.settings.keys()) // self.columns + 2)
        for index, name in enumerate(self.settings.keys()):
            row = index % rows
            col = index // rows
            self.grid_layout.addWidget(self.settings[name], row, col)

    def resizeEvent(self, event):
        """Recalculate columns when resizing."""
        new_width = self.scroll_area.viewport().width()
        self.columns = max(1, new_width // (self.cell_width))  # Adjust based on available space
        self.update_grid()
        super().resizeEvent(event)


