from typing import is_typeddict
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtNetwork import QNetworkReply
from PySide6.QtWidgets import QCheckBox, QFrame, QHBoxLayout, QLineEdit, QScrollArea, QSizePolicy, QTreeView, QTreeWidget, QTreeWidgetItem, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import QAbstractItemModel, QModelIndex, QPersistentModelIndex, Qt, Slot
import json
from functools import partial

from App.inputs import BoolInput, Input, IntInput, StringInput


from .server_client import ServerClient
from TaskManagerServer.Backend.types import Module, ModuleTemplate
from App.styles import BG1, BORDER


class ModuleValueNode(QWidget):

    def __init__(self, text: str, input: Input, parent=None) -> None:
        super().__init__(parent)

        self.input = input
        self.text = text

        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(f"background-color: transparent; border: none;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)
        self.setSizePolicy(self.sizePolicy().Policy.Expanding, self.sizePolicy().Policy.Expanding)

        label = QLabel(self.text)
        layout.addWidget(label, 2)

        layout.addStretch()
        layout.addWidget(self.input, 4)

    def get_value(self):
        return self.input.get_value()


class ModuleTree(QTreeWidget):

    def __init__(self, show_external_settings: bool = True, parent=None) -> None:
        super().__init__(parent)

        self.setHeaderHidden(True)
        self.setEditTriggers(QTreeView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QTreeWidget.SelectionMode.NoSelection)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # self.setColumnCount(2)
        # self.collapseAll()
        self.expandAll()


    def add_module(self, module: Module | ModuleTemplate):
        module_item = QTreeWidgetItem(self)
        module_item.setText(0, "")
        self.addTopLevelItem(module_item)
        module_widget = ModuleValueNode(module.name, BoolInput(False))
        self.setItemWidget(module_item, 0, module_widget)

        # internal settings:
        internal_settings = module.internal_settings
        internal_settings_item = QTreeWidgetItem(module_item)
        internal_settings_item.setText(0, "Internal Settings")

        num_cores_item = QTreeWidgetItem(internal_settings_item)
        num_cores_item.setText(0, "")
        module_item.addChild(num_cores_item)
        if type(internal_settings.num_cores) == int:
            widget = ModuleValueNode("NumCores", IntInput(internal_settings.num_cores,
                                                          min_value=1, max_value=32))
        else:
            widget = ModuleValueNode("NumCores", StringInput(internal_settings.num_cores))

        self.setItemWidget(num_cores_item, 0, widget)

        
        # server stats
        if isinstance(module, Module):
            item = QTreeWidgetItem(module_item)
            item.setText(0, "")
            module_item.addChild(item)
            widget = ModuleValueNode("ModuleID", StringInput(module.module_id, False))
            self.setItemWidget(item, 0, widget)

            item = QTreeWidgetItem(module_item)
            item.setText(0, "")
            module_item.addChild(item)
            widget = ModuleValueNode("Finished", BoolInput(module.finished, False))
            self.setItemWidget(item, 0, widget)


        self.header().setStretchLastSection(True)



class ModulesView(QWidget):

    def __init__(self, parent_task_id: str, modules: list[ModuleTemplate], client: ServerClient, parent=None) -> None:
        super().__init__(parent)

        self.parent_task_id = parent_task_id
        self.modules = modules
        self.client = client

        self.module_objects = {}

        self.init_ui()

        if self.parent_task_id:
            self.fetch_modules()
        elif self.modules:
            self.update_modules(self.modules)


    def init_ui(self):
        self.setMinimumSize(300, 200)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("border: none;")

        label = QLabel("modules")
        main_layout.addWidget(label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setStyleSheet(f"border: 1px solid {BORDER};")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        modules_container = QWidget()
        self.scroll_area_layout = QVBoxLayout(modules_container)
        self.scroll_area_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.setWidget(modules_container)


        self.tree = ModuleTree()
        self.scroll_area_layout.addWidget(self.tree, 1)
        self.scroll_area_layout.addStretch()


        main_layout.addWidget(self.scroll_area)


    def fetch_modules(self):
        reply = self.client.get_all_modules(self.parent_task_id)
        reply.finished.connect(partial(self.process_server_reply, reply))

    @Slot()
    def process_server_reply(self, reply: QNetworkReply):
        data = json.loads(bytes(reply.readAll().data()).decode("utf-8"))
        reply.deleteLater()
        modules = [Module(**d) for d in data]
        self.update_modules(modules)


    def update_modules(self, modules: list[Module] | list[ModuleTemplate]):
        # clear_layout(self.scroll_area_layout)
        for module in modules:
            self.tree.add_module(module)
        self.scroll_area_layout.addStretch()
