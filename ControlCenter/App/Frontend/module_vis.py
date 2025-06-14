from PySide6.QtWidgets import (
    QHBoxLayout,
    QCheckBox,
    QLabel,
    QTreeWidgetItem,
    QSpacerItem,
    QSizePolicy,
)
from PySide6.QtCore import QThread
from .helper import ScrollablePopUp
from App.Backend.module import Module
from App.Backend.settings import Setting
from App.Backend.parser import load_modules_from_file
from .setting_vis import SettingObject
from .helper import TreeNode, StatusIndicator


class ModuleObject(TreeNode):
    def __init__(self, module: Module):
        super().__init__()
        self.module = module
        self.external_settings: list[SettingObject] = []
        self.internal_settings: list[SettingObject] = []

        self.module.process.output_received.connect(self.handle_output)
        self.module.process.program_error_received.connect(self.handle_error)
        self.module.process.finished.connect(self.process_finished)

        self.init_ui()

    def init_ui(self):
        node = QLabel(self.module.name)
        self.add_object([node])
        for setting in self.module.settings:
            setting_object = SettingObject(setting)
            self.add_child(setting_object)
            self.external_settings.append(setting_object)

        priority_setting_object = SettingObject(self.module.priority)
        self.add_child(priority_setting_object)
        self.internal_settings.append(priority_setting_object)

        self.header_layout.addStretch()
        self.status_circle = StatusIndicator(diameter=10)
        self.add_object([self.status_circle])
        self.header_layout.addSpacerItem(
            QSpacerItem(5, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        )

    def handle_output(self, text: str):
        print(text)

    def handle_error(self, text: str):
        self.module.running = False
        print(text)

    def process_finished(self, exit_code: str):
        self.module.running = False
        self.module.finished = True
        print(exit_code)

    def run(self):
        self.module.running = True
        self.worker = QThread()
        self.module.process.moveToThread(self.worker)
        self.worker.started.connect(self.module.run)

        self.module.process.output_received.connect(self.handle_output)
        self.module.process.program_error_received.connect(self.handle_error)
        self.module.process.finished.connect(self.process_finished)

        self.module.process.finished.connect(self.worker.quit)
        self.worker.finished.connect(self.worker.deleteLater)

        self.worker.start()


class PopUpModuleSelection(ScrollablePopUp):
    def __init__(self, parent=None, exclude: list[Module] | None = None):
        super().__init__(parent=parent)
        self.setWindowTitle("Select Modules")

        self.checkboxes = {}
        self.modules = load_modules_from_file("modules.yaml")
        if exclude is not None:
            excluded = [m.name for m in exclude]
            self.modules = [m for m in self.modules if m.name not in excluded]

    def run(self):
        if self.modules:
            self.init_ui(self.modules)
            return self.exec()
        return False

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

    def get_selected(self):
        return [m for m in self.checkboxes if self.checkboxes[m]]

    def on_click(self, event, module):
        self.checkboxes[module].toggle()
