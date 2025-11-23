import os
import stat
from typing import Optional
from PySide6.QtGui import Qt
from PySide6.QtWidgets import (
    QDialog, QHeaderView, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QHBoxLayout, QPushButton, QComboBox
)
from .server_client import ServerClient

class ServerFileDialog(QDialog):
    def __init__(self, server_client: ServerClient, path: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select File")

        self.server_client = server_client

        self.current_path = path

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Name", "Type"])
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tree.itemDoubleClicked.connect(self.enter_item)

        btn_select = QPushButton("Select")
        btn_select.clicked.connect(self.accept)

        layout = QVBoxLayout(self)
        hl = QHBoxLayout()
        layout.addLayout(hl)
        layout.addWidget(self.tree)
        layout.addWidget(btn_select)

        self.refresh()

    def refresh(self):
        self.tree.clear()
        entries = self.server_client.list_dir(self.current_path)
        entries.sort()
        for name, full, is_dir in entries:
            item = QTreeWidgetItem([name, "Dir" if is_dir else "File"])
            item.setData(0, 32, full)  # store full path
            self.tree.addTopLevelItem(item)

    def enter_item(self, item):
        full = item.data(0, 32)
        if item.text(1) == "Dir":
            self.current_path = full
            self.refresh()

    def selected_path(self):
        item = self.tree.currentItem()
        if item:
            return item.data(0, 32)
        return None
