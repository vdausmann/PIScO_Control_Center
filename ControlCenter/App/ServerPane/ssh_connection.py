from PySide6.QtCore import QObject
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QLabel
)
import subprocess
import paramiko

class SSHConnectionClient:

    def __init__(self) -> None:
        self.ssh_client: paramiko.SSHClient | None = None

    def connect(self, username: str, host: str, port: int = 22):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh_client.connect(host, port=port, username=username, timeout=5)
            return True, None
        except Exception as e:
            return False, e

    def disconnect(self):
        if self.ssh_client is not None:
            self.ssh_client.close()
            self.connected = False

    def run_command(self, command: str) -> tuple[str, str]:
        if self.ssh_client is None:
            QMessageBox.warning(None, "Not connected", "Please connect first.")
            return "", ""
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        return output, error

    def start_port_forward(self, local_port: int, remote_host: str, remote_port: int,
                           username: str, host: str):
        """Forward local_port → remote_host:remote_port through the SSH tunnel."""
        cmd = [
            "ssh",
            "-L", f"{local_port}:{remote_host}:{remote_port}",
            f"{username}@{host}",
            "-N"  # No remote command, just forwarding
        ]

        proc = subprocess.Popen(cmd)
        return proc  # You can later call proc.terminate()


class SSHConnectionDialog(QDialog):
    def __init__(self, ssh_client: SSHConnectionClient, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SSH Connection")
        self.setMinimumWidth(300)

        self.ssh_client = ssh_client

        # --- Input fields ---
        self.host_input = QLineEdit()
        self.port_input = QLineEdit()
        self.port_input.setText("22")  # Default SSH port
        self.username_input = QLineEdit()

        form_layout = QFormLayout()
        form_layout.addRow("Host:", self.host_input)
        form_layout.addRow("Port:", self.port_input)
        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Password:", QLabel("Please set up a SSH key for the connection"))

        # --- Buttons ---
        self.connect_button = QPushButton("Connect")
        self.cancel_button = QPushButton("Cancel")
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.cancel_button)

        # --- Layout ---
        layout = QVBoxLayout(self)
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)

        # --- Connections ---
        self.connect_button.clicked.connect(self.try_connect)
        self.cancel_button.clicked.connect(self.reject)

    def try_connect(self):
        host = self.host_input.text().strip()
        port = int(self.port_input.text().strip() or 22)
        username = self.username_input.text().strip()

        success, exception = self.ssh_client.connect(username, host, port)
        if success:
            QMessageBox.information(self, "Success", f"Connected to {host}.")
            self.accept()
        else:
            QMessageBox.critical(self, "Connection Failed", f"SSH connection failed: {exception}")

