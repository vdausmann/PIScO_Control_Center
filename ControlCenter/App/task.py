from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QFrame, QDialog, QVBoxLayout, QPushButton, QCheckBox, QScrollArea, QGridLayout, QLineEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent, QIcon
from .module import Module
from .helper import ScrollablePopUp, DropdownSettings
# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#     from .app import PIScOControlCenter

class Task: 
    def __init__(self, selected_modules: dict[str, bool]):
        self.selected_modules = selected_modules
        self.modules: list[Module] = []
        self.finished: dict[str, bool] = {m: False for m in self.selected_modules if self.selected_modules[m]}
        self.running_module = ""

    def add_module(self, module: Module):
        if not self.selected_modules[module.name]:
            self.selected_modules[module.name] = True
            self.modules.append(module)
        else:
            print("Module already in module list")


class TaskObject(QWidget):
    def __init__(self, name: str, selected_modules: dict[str, bool], app):
        super().__init__()
        self.name = name
        self.app = app
        self.selected = False  # Track selection state
        self.task = Task(selected_modules)
        self.init_ui()

    def init_ui(self):
        self.toggled = False
        self.setMinimumSize(1000, 30)  # Fixed size to trigger horizontal scrollbar
        self.setFixedHeight(30)

        # Background & border
        self.setStyleSheet("""
            QWidget {
                background-color: #c0c0c0;
                border-radius: 4px;
                border: 1px solid #a0a0a0;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        frame = QFrame(self)

        frame_layout = QHBoxLayout(frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(5)

        self.dropDownMenu = DropdownSettings()
        frame_layout.addWidget(self.dropDownMenu, alignment=Qt.AlignmentFlag.AlignLeft)
        self.dropDownMenu.add_action_from_label("test", lambda: None)
        self.dropDownMenu.add_action_from_label("\033[91mDelete Task\033[0m", lambda: self.app.delete_task(self.name))


        # Label
        self.label = QLabel(self.name)
        self.label.setStyleSheet("font-size: 10pt; border: none;")
        frame_layout.addWidget(self.label, 1)

        # Make label clickable by overriding mousePressEvent
        self.label.mousePressEvent = self.label_clicked

        frame.setLayout(frame_layout)
        layout.addWidget(frame, 1)

    def label_clicked(self, ev: QMouseEvent):
        self.toggled = not self.toggled
        self.toggle_selection()

    def toggle_selection(self):
        self.update_style()

    def update_style(self):
        if self.toggled:
            self.setStyleSheet("""
                QWidget {
                    background-color: #d0e8ff;  /* Light blue for selection */
                    border-radius: 4;
                    border: 2px solid #79aee2;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #e6f0f8;
                    border-radius: 4;
                    border: 1px solid #c0d3e5;
                }
            """)

class PopUpTaskSettings(ScrollablePopUp):
    def __init__(self, module: Module, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Settings")
        self.inputs = {}  # To store input widgets
        self.module = module
        self.init_ui()

    def init_ui(self):
        rows = []
        settings = self.module.get_settings()
        for setting in settings:
            try:
                kind, value = settings[setting]
            except:
                kind = settings[setting]
                value = None

            row = QHBoxLayout()
            label = QLabel(setting)
            if kind == "bool":
                input_widget = QCheckBox()
                if not value is None:
                    input_widget.setChecked(value)
                row.addWidget(label, 1)
                row.addWidget(input_widget)
            else:  # 'text'
                input_widget = QLineEdit()
                if not value is None:
                    input_widget.setText(value)
                row.addWidget(label)
                row.addWidget(input_widget, 1)

            self.inputs[setting] = input_widget
            rows.append(("", row))

        self.add_rows(rows)

    def get_settings(self):
        result = {}
        for name, widget in self.inputs.items():
            if isinstance(widget, QCheckBox):
                result[name] = widget.isChecked()
            else:
                result[name] = widget.text()
        return result
