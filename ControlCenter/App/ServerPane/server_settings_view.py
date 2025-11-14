from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QLabel, QSplitter, QFormLayout, QLineEdit, QTextEdit,
        QPushButton, QCheckBox
)
from PySide6.QtGui import QIntValidator, Qt
from PySide6.QtCore import Qt
from App.Resources.styles import BORDER

from .ssh_settings_view import SSHConnectionSettings
from Server.Client import ServerClient, SSHConnectionClient

class ServerSettingsView(QWidget):
    def __init__(self, client: ServerClient):
        super().__init__()
        self.client = client

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        split = QSplitter(Qt.Orientation.Vertical)
        main_layout.addWidget(split)
        ########################################
        ## Server settings:
        ########################################
        server_settings = QWidget()
        server_settings.setStyleSheet("border: none")
        server_settings_layout = QVBoxLayout(server_settings)
        split.addWidget(server_settings)

        settings = QFormLayout()
        label = QLabel("Server settings")
        label.setStyleSheet("font-size: 16px;")
        server_settings_layout.addWidget(label,
                                         alignment=Qt.AlignmentFlag.AlignCenter)
        server_settings_layout.addLayout(settings)

        self.host_edit = QLineEdit()
        self.host_edit.setStyleSheet(f"border: 1px solid {BORDER};")
        self.host_edit.textChanged.connect(self.host_edit_changed)
        self.host_edit.setText(self.client.host)
        settings.addRow("Host:", self.host_edit)

        self.port_edit = QLineEdit()
        self.port_edit.setValidator(QIntValidator(1024, 49151))
        self.port_edit.textChanged.connect(self.port_edit_changed)
        self.port_edit.setText(str(self.client.port))
        self.port_edit.setStyleSheet(f"border: 1px solid {BORDER};")
        settings.addRow("Port:", self.port_edit)

        self.path_to_server_script = QLineEdit()
        self.path_to_server_script.textChanged.connect(self.path_to_server_script_changed)
        self.path_to_server_script.setText("/home/tim/Documents/Arbeit/PIScO_Control_Center/ControlCenter/start_server.sh")
        self.path_to_server_script.setStyleSheet(f"border: 1px solid {BORDER};")
        settings.addRow("Path to server script (remote or local):", self.path_to_server_script)

        ########################################
        ## Remote:
        ########################################
        self.remote_checkbox = QCheckBox()
        self.remote_checkbox.stateChanged.connect(self.remote_checkbox_changed)
        settings.addRow("Remote:", self.remote_checkbox)

        self.ssh_connection_settings = SSHConnectionSettings(self.client.ssh_client)
        self.ssh_connection_settings.setDisabled(True)
        server_settings_layout.addWidget(self.ssh_connection_settings)
        server_settings_layout.addStretch()

        ########################################
        ## Buttons:
        ########################################
        self.start_server_button = QPushButton("Start server")
        self.start_server_button.clicked.connect(self.client.start_server)
        server_settings_layout.addWidget(self.start_server_button)

        self.disconnect_button = QPushButton("Disconnect")
        server_settings_layout.addWidget(self.disconnect_button)

        self.stop_server_button = QPushButton("Stop Server")
        self.stop_server_button.setObjectName("DeleteButton")
        server_settings_layout.addWidget(self.stop_server_button)
        self.stop_server_button.clicked.connect(self.client.stop_server)
            
        ########################################
        ## Websocket:
        ########################################
        websocket_area = QWidget()
        websocket_area_layout = QVBoxLayout(websocket_area)
        split.addWidget(websocket_area)

        websocket_output_label = QLabel("Websocket Output:")
        websocket_output_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        websocket_area_layout.addWidget(websocket_output_label)

        self.websocket_output = QTextEdit()
        self.websocket_output.setReadOnly(True)
        self.websocket_output.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        websocket_area_layout.addWidget(self.websocket_output)

    def host_edit_changed(self):
        text = self.host_edit.text()
        if not text:
            self.client.host = None
        else:
            self.client.host = text

    def port_edit_changed(self):
        text = self.port_edit.text()
        if not text:
            self.client.port = None
            self.port_edit.setStyleSheet("color: #222222;")
        else:
            if self.port_edit.validator().validate(text, 0)[0] == QIntValidator.State.Acceptable:
                self.client.port = int(text)
                self.port_edit.setStyleSheet("color: #222222;")
            else:
                self.port_edit.setStyleSheet("color: red;")

    def remote_checkbox_changed(self):
        self.client.remote = self.remote_checkbox.isChecked()
        self.ssh_connection_settings.setDisabled(not self.client.remote)

    def path_to_server_script_changed(self):
        self.client.path_to_server_script = self.path_to_server_script.text()

