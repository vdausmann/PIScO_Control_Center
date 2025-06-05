from PySide6.QtWidgets import (QWidget, QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QLabel, QPushButton,
QScrollArea)
from .helper import ScrollablePopUp

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


class PopUpModuleSelection(ScrollablePopUp):
    def __init__(self, modules: list[str], parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Select Modules")

        self.checkboxes = {}
        self.init_ui(modules)

    def init_ui(self, modules):
        rows = []
        for module in modules:
            row = QHBoxLayout()
            checkbox = QCheckBox()
            label = QLabel(text=module)
            row.addWidget(label, 1)
            row.addWidget(checkbox)
            rows.append((module, row))
            self.checkboxes[module] = checkbox
        self.add_rows(rows, self.on_click)

    def get_selected(self) -> dict[str, bool]:
        return {module: self.checkboxes[module].isChecked() for module in self.checkboxes}

    def on_click(self, event, module):
        self.checkboxes[module].toggle()
