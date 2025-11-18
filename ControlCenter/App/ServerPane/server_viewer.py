from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QLabel, QSplitter
)
from PySide6.QtCore import QTimer, Qt

from .fast_api_view import FastAPIView
from .server_settings_view import ServerSettingsView
from Server.Client import ServerClient
from App.Resources.styles import BORDER

class ServerViewer(QWidget):
    def __init__(self, client: ServerClient):
        super().__init__()

        self.client = client
        self.client.server_status_signal.connect(lambda x: print("Server running:", x))

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        self.setStyleSheet(f"border: 1px solid {BORDER};")

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter, 1)

        ########################################
        ## Server settings:
        ########################################
        self.server_settings_view = ServerSettingsView(self.client)
        self.splitter.addWidget(self.server_settings_view)


        ########################################
        ## FastAPI connection:
        ########################################
        self.fast_api_view = FastAPIView(self.client)
        self.splitter.addWidget(self.fast_api_view)
        self.splitter.setSizes([300, 700])


