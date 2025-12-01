from subprocess import run
from PySide6.QtCore import Slot
from PySide6.QtGui import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (QCheckBox, QFormLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QSplitter, QTextEdit,
QVBoxLayout, QWidget)

from App.helper import LoadingSpinner

from Server.Client import ServerClient


class FastAPIView(QWidget):

    def __init__(self, client: ServerClient, parent=None) -> None:
        super().__init__(parent)

        self.web_view_loaded = False
        self.loading = False

        self.client = client
        self.client.start_up_signal.connect(self.show_loading)
        self.client.server_started.connect(self._on_server_status)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.load_button = QPushButton("Load")
        self.load_button.clicked.connect(self._load)

        self.web_view = QWebEngineView()
        self.web_view.hide()

        self.loading_spinner = LoadingSpinner()
        layout.addWidget(self.loading_spinner, alignment=Qt.AlignmentFlag.AlignCenter)
        self.loading_spinner.hide()


        layout.addWidget(self.web_view, 1)
        layout.addStretch()
        layout.addWidget(self.load_button)


    def _load(self):
        if not self.web_view_loaded:
            self.load()
        else:
            self.unload()

    @Slot(bool)
    def _on_server_status(self, running: bool):
        print("Status", running)
        if running and self.loading:
            self.show_loading(False)
            self.load()
        elif not running and self.web_view_loaded:
            self.unload()
        elif running:
            self.load()


    @Slot(bool)
    def show_loading(self, activate: bool):
        if activate:
            self.loading = True
            self.loading_spinner.show()
            self.loading_spinner.toggle(True)
        else:
            self.loading = False
            self.loading_spinner.hide()
            self.loading_spinner.toggle(False)

    def load(self):
        if not self.client.port is None and not self.client.host is None:
            self.load_button.setText("Close")
            self.web_view.load(f"http://{self.client.host}:{self.client.port}/docs")
            self.web_view.show()
            self.web_view_loaded = True
        else:
            dlg = QMessageBox(QMessageBox.Icon.Warning,
            "FAST-API warning", "Server not started or no host and/or port specified!")
            dlg.exec()


    def unload(self):
        self.load_button.setText("Load")
        self.web_view.close()
        self.web_view.hide()
        self.web_view_loaded = False
