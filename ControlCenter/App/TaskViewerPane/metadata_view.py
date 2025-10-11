from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QScrollArea, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

from .server_client import ServerClient
from App.helper import clear_layout
from App.styles import BORDER



class MetadataView(QWidget):

    def __init__(self, metadata: dict, client: ServerClient, parent=None) -> None:
        super().__init__(parent)

        self.metadata = metadata
        self.client = client

        self.init_ui()
        self.update_data(self.metadata)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("border: none;")

        label = QLabel("metadata")
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

    def update_data(self, data: dict):
        # self.metadata = data

        clear_layout(self.scroll_area_layout)

        for key in data:
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row.setStyleSheet("border: none;")
            row_layout.setContentsMargins(2, 2, 2, 2)
            label = QLabel(key)
            value = QLineEdit(str(data[key]))
            value.setStyleSheet("border: 1px solid;")

            row_layout.addWidget(label, 1)
            row_layout.addStretch()
            row_layout.addWidget(value, 2)
            self.scroll_area_layout.addWidget(row)

        self.scroll_area_layout.addStretch()


