from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QFrame, QDialog, QVBoxLayout, QPushButton, QCheckBox, QScrollArea, QGridLayout, QLineEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent
from .module import Module


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
    def __init__(self, name: str, selected_modules: dict[str, bool]):
        super().__init__()
        self.name = name
        self.selected = False  # Track selection state
        self.init_ui()

    def init_ui(self):
        self.toggled = False
        self.setMinimumSize(1000, 30)  # Fixed size to trigger horizontal scrollbar
        self.setFixedHeight(30)

        # Background & border
        self.setStyleSheet("""
            QWidget {
                background-color: #e6f0f8;
                border-radius: 4px;
                border: 1px solid #c0d3e5;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        frame = QFrame(self)
        # frame.setStyleSheet("background-color: #000;")
        frame_layout = QHBoxLayout(frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(0)

        # Label
        self.label = QLabel(self.name)
        self.label.setStyleSheet("font-size: 10pt;")
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

class PopUpTaskSettings(QDialog):
    def __init__(self, module: Module, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.row_height = 30
        self.window_height = 400
        self.window_width = 200
        self.padding = 2
        self.setFixedSize(self.window_width, self.window_height)
        self.inputs = {}  # To store input widgets
        self.module = module
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        label = QLabel(f"Settings for {self.module.name}")
        main_layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        rows_layout = QVBoxLayout(scroll_widget)
        rows_layout.setContentsMargins(2, 0, 2, 0)
        rows_layout.setSpacing(5)

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
            rows_layout.addLayout(row)

        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)

        # OK / Cancel buttons
        button_row = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_row.addStretch()
        button_row.addWidget(ok_btn)
        button_row.addWidget(cancel_btn)
        main_layout.addLayout(button_row)

    def get_settings(self):
        result = {}
        for name, widget in self.inputs.items():
            if isinstance(widget, QCheckBox):
                result[name] = widget.isChecked()
            else:
                result[name] = widget.text()
        return result
