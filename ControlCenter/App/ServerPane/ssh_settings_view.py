from PySide6.QtCore import QObject
from PySide6.QtGui import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QLabel
)

from App.Resources.styles import BORDER
from Server.Client import SSHConnectionClient


class SSHConnectionSettings(QWidget):
    def __init__(self, ssh_client: SSHConnectionClient, parent=None):
        super().__init__(parent)
        self.ssh_client = ssh_client

        self.init_ui()

    def init_ui(self):
        # --- Input fields ---
        self.host_input = QLineEdit()
        self.host_input.setStyleSheet(f"border: 1px solid {BORDER};")
        self.host_input.setText("192.168.178.59")
        self.port_input = QLineEdit()
        self.port_input.setStyleSheet(f"border: 1px solid {BORDER};")
        self.port_input.setText("22")  # Default SSH port
        self.username_input = QLineEdit()
        self.username_input.setText("tim")
        self.username_input.setStyleSheet(f"border: 1px solid {BORDER};")

        ssh_connection_label = QLabel("SSH connection")
        ssh_connection_label.setStyleSheet("font-size: 16px;")
        ssh_connection_form_layout = QFormLayout()
        ssh_connection_form_layout.addRow("IP:", self.host_input)
        ssh_connection_form_layout.addRow("Port:", self.port_input)
        ssh_connection_form_layout.addRow("Username:", self.username_input)
        ssh_connection_form_layout.addRow("Password:", QLabel("Please set up a SSH key for the connection"))

        port_forwarding_label = QLabel("Port forwarding", alignment=Qt.AlignmentFlag.AlignCenter)
        port_forwarding_label.setStyleSheet("font-size: 16px;")
        port_forwarding_form_layout = QFormLayout()
        self.local_port_input = QLineEdit("8000")
        self.local_port_input.setStyleSheet(f"border: 1px solid {BORDER};")
        self.remote_port_input = QLineEdit("8000")
        self.remote_port_input.setStyleSheet(f"border: 1px solid {BORDER};")
        self.remote_host_input = QLineEdit("127.0.0.1")
        self.remote_host_input.setStyleSheet(f"border: 1px solid {BORDER};")
        port_forwarding_form_layout.addRow("Local port:", self.local_port_input)
        port_forwarding_form_layout.addRow("Remote port:", self.remote_port_input)
        port_forwarding_form_layout.addRow("Remote host:", self.remote_host_input)


        # --- Buttons ---
        self.connect_button = QPushButton("Connect SSH")
        self.disconnect_button = QPushButton("Disconnect SSH")
        self.disconnect_button.setObjectName("DeleteButton")

        # --- Layout ---
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(ssh_connection_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(ssh_connection_form_layout)
        layout.addWidget(port_forwarding_label)
        layout.addLayout(port_forwarding_form_layout)
        layout.addWidget(self.connect_button)
        layout.addWidget(self.disconnect_button)

        # --- Connections ---
        self.connect_button.clicked.connect(self._connect)
        self.disconnect_button.clicked.connect(self._disconnect)

    def _connect(self):
        host = self.host_input.text().strip()
        port = int(self.port_input.text().strip() or 22)
        username = self.username_input.text().strip()

        local_port = int(self.local_port_input.text().strip())
        remote_port = int(self.remote_port_input.text().strip())
        remote_host = self.remote_host_input.text()

        success, exception = self.ssh_client.connect(username, host, port)
        if success:
            self.ssh_client.start_port_forwarding(local_port, remote_host, remote_port, username, host)
            QMessageBox.information(self, "Success", f"Connected to {host}.")
        else:
            QMessageBox.critical(self, "Connection Failed", f"SSH connection failed: {exception}")

    def _disconnect(self):
        success = self.ssh_client.disconnect()
        if success:
            QMessageBox.information(self, "Disconnected", f"Closed ssh connection.")

