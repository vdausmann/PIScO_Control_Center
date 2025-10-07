from os import replace
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QScrollArea, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

from .server_client import ServerClient
from Server.Backend.types import ModuleTemplate
from App.helper import clear_layout
from App.styles import BORDER


class ModulesView(QWidget):

    def __init__(self, modules: list[str] | list[ModuleTemplate], client: ServerClient, parent=None) -> None:
        super().__init__(parent)

        self.modules = modules
        self.client = client

        self.init_ui()
        self.fetch_modules()

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

        meta_data_container = QWidget()
        self.scroll_area_layout = QVBoxLayout(meta_data_container)
        self.scroll_area_layout.setContentsMargins(4, 2, 4, 2)
        self.scroll_area.setWidget(meta_data_container)

        main_layout.addWidget(self.scroll_area)

    def fetch_modules(self):
        for module_id in self.modules:
            if not type(module_id) == str:
                continue
            reply = self.client.get_module(module_id)
            reply.finished.connect(lambda: print(bytes(reply.readAll()).decode()))
