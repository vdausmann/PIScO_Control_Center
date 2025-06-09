from PySide6.QtWidgets import QHBoxLayout, QCheckBox, QLabel, QTreeWidgetItem
from .helper import ScrollablePopUp
from App.Backend.module import Module
from App.Backend.settings import Setting
from .setting_vis import SettingObject
from .helper import TreeNode


class ModuleObject(TreeNode):
    def __init__(self, module: Module):
        super().__init__()
        self.module = module
        self.init_ui()

    def init_ui(self):
        node = QLabel(self.module.name)
        self.add_object([node])
        for setting in self.module.settings:
            setting_object = SettingObject(setting)
            self.add_child(setting_object)

        priority_setting_object = SettingObject(self.module.priority)
        self.add_child(priority_setting_object)


class PopUpModuleSelection(ScrollablePopUp):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Select Modules")

        self.checkboxes = {}
        # modules = load_modules_from_file("modules.cfg")
        modules = []
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
