from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtNetwork import QNetworkReply
from PySide6.QtWidgets import QCheckBox, QFrame, QHBoxLayout, QLineEdit, QScrollArea, QSizePolicy, QTreeView, QTreeWidget, QTreeWidgetItem, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import QAbstractItemModel, QModelIndex, QPersistentModelIndex, Qt, Slot
import json
from functools import partial


from .server_client import ServerClient
from TaskManagerServer.Backend.types import Module, ModuleTemplate
from App.styles import BG1, BORDER


class ModuleValueNode(QWidget):

    def __init__(self, text: str, value, parent=None) -> None:
        super().__init__(parent)

        self.value = value
        self.text = text

        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)
        self.setSizePolicy(self.sizePolicy().Policy.Expanding, self.sizePolicy().Policy.Expanding)

        self.setObjectName("parentWidget")
        self.setStyleSheet(f"#parentWidget > QWidget {{ background-color: {BG1}; border: none;}}")
        # self.setStyleSheet(f"background-color: transparent;")

        label = QLabel(self.text)
        layout.addWidget(label, 2)
        
        if isinstance(self.value, bool):
            self.value_input = QCheckBox()
            self.value_input.setChecked(self.value)
            self.value_input.setFixedSize(15, 15)
        else:
            self.value_input = QLineEdit(str(self.value))
        self.value_input.setStyleSheet(f"border: 1px solid {BORDER};")

        layout.addStretch()
        layout.addWidget(self.value_input)

    def get_value(self):
        if isinstance(self.value_input, QCheckBox):
            return self.value_input.isChecked
        else:
            return self.value_input.text()

class ModuleTree(QTreeWidget):

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setHeaderHidden(True)
        self.setEditTriggers(QTreeView.EditTrigger.NoEditTriggers)
        # self.collapseAll()
        self.expandAll()


    def add_module(self, module: Module | ModuleTemplate):
        module_item = QTreeWidgetItem(self)
        module_item.setText(0, "")
        self.addTopLevelItem(module_item)
        module_widget = ModuleValueNode(module.name, False)
        self.setItemWidget(module_item, 0, module_widget)


        finished_item = QTreeWidgetItem(self)
        finished_item.setText(0, "Test")
        module_item.addChild(finished_item)
        # finished_widget = ModuleValueNode("Finished", False)
        # self.setItemWidget(finished_item, 0, finished_widget)

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
