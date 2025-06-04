from PySide6.QtWidgets import (QWidget, QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QLabel, QPushButton,
QScrollArea)

class Module:
    def __init__(self, name: str):
        self.name = name
        self.settings = []

    def load_settings(self, default=True):
        ...

    def get_settings(self):
        return {
            "Enable Logging": ["bool", True],
            "Username": ["text", "tim"],
            "Auto Save": ["bool", False],
            "Max Retries": ["text", None]
        }

    def run(self):
        ...


class PopUpModuleSelection(QDialog):
    def __init__(self, modules: list[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Modules")
        self.row_height = 30
        self.window_height = 400
        self.window_width = 200
        self.padding = 2
        self.setFixedSize(self.window_width, self.window_height)

        self.checkboxes = {}
        self.init_ui(modules)

    def init_ui(self, modules):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(self.padding)


        for module in modules:
            widget = QWidget()
            widget.setFixedSize(self.window_width, self.row_height)
            widget.setStyleSheet("background-color: #888;")

            row = QHBoxLayout(widget)
            checkbox = QCheckBox()
            label = QLabel(text=module)
            row.addWidget(label, 1)
            row.addWidget(checkbox)
            
            widget.setLayout(row)
            scroll_layout.addWidget(widget)
            self.checkboxes[module] = checkbox
            widget.mousePressEvent = lambda event, m=module: self.on_click(m)


        for _ in range(len(modules), self.window_height // (self.row_height + self.padding) - 1):
            widget = QWidget()
            widget.setStyleSheet("background: transparent;")
            widget.setFixedSize(self.window_width, self.row_height)
            scroll_layout.addWidget(widget)

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        button_row = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_row.addStretch()
        button_row.addWidget(ok_button)
        button_row.addWidget(cancel_button)
        layout.addLayout(button_row)

    def get_selected(self) -> dict[str, bool]:
        return {module: self.checkboxes[module].clicked for module in self.checkboxes}

    def on_click(self, module):
        self.checkboxes[module].toggle()
