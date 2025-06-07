from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QFrame,
    QDialog,
    QVBoxLayout,
    QPushButton,
    QCheckBox,
    QScrollArea,
    QGridLayout,
    QLineEdit,
    QTreeWidgetItem,
    QTreeWidget,
    QAbstractItemView,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent, QIcon
from .module import Module
from .helper import ScrollablePopUp, DropdownSettings
# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#     from .app import PIScOControlCenter


class Task:
    def __init__(self, modules: list[Module]):
        self.modules = modules

    def add_module(self, module: Module):
        if not self.selected_modules[module.name]:
            self.selected_modules[module.name] = True
            self.modules.append(module)
        else:
            print("Module already in module list")


class TaskObject(QTreeWidgetItem):
    def __init__(self, name: str, modules: list[Module], app):
        super().__init__([name])
        self.name = name
        self.app = app
        self.task = Task(modules)
        self.init_ui()

    def init_ui(self):
        self.app.tree.addTopLevelItem(self)
        # for module in self.task.modules:
            # print(module.name)
            # module_item = QTreeWidgetItem([module.name])
            # for setting in module.settings:
            #     ...
            # self.addChild(module_item)


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
