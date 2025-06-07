from PySide6.QtWidgets import QHBoxLayout, QCheckBox, QLabel, QMessageBox
from .helper import ScrollablePopUp
from .settings import Setting


class Module:
    def __init__(self, name: str):
        self.name = name
        self.settings: list[Setting] = []

    def load_settings(self, default=True): ...

    def run(self): ...




class PopUpModuleSelection(ScrollablePopUp):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Select Modules")

        self.checkboxes = {}
        modules = load_modules_from_file("modules.cfg")
        self.init_ui(modules)

    def init_ui(self, modules):
        rows = []
        for module in modules:
            row = QHBoxLayout()
            checkbox = QCheckBox()
            label = QLabel(text=module.name)
            row.addWidget(label, 1)
            row.addWidget(checkbox)
            rows.append((module, row))
            self.checkboxes[module] = checkbox
        self.add_rows(rows, self.on_click)

    def get_selected(self) -> dict[str, bool]:
        return {
            module: self.checkboxes[module].isChecked() for module in self.checkboxes
        }

    def on_click(self, event, module):
        self.checkboxes[module].toggle()
