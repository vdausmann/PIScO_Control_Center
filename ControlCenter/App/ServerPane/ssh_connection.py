from PySide6.QtCore import QObject
from PySide6.QtGui import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QLabel
)
import subprocess
import paramiko

from App.Resources.styles import BORDER

class SSHConnectionClient:

    def __init__(self) -> None:
        self.ssh_client: paramiko.SSHClient | None = None
        self.ssh_port_forwarding_process: subprocess.Popen | None = None

    def connect(self, username: str, host: str, port: int = 22):
        # Already connected
        if self.ssh_client is not None:
            QMessageBox.information(None, "Already connected", "Already connected via ssh.")
            return True, None

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
            self.ssh_client = None

    def run_command(self, command: str) -> tuple[str, str]:
        if self.ssh_client is None:
            QMessageBox.warning(None, "Not connected", "Please connect first.")
            return "", ""
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        return output, error

    def start_port_forwarding(self, local_port: int, remote_host: str, remote_port: int,
                           username: str, host: str):
        """Forward local_port → remote_host:remote_port through the SSH tunnel."""
        if self.ssh_port_forwarding_process is not None:
            QMessageBox.information(None, "Already connected", "Port forwarding process already running")
            return 

        cmd = [
            "ssh",
            "-L", f"{local_port}:{remote_host}:{remote_port}",
            f"{username}@{host}",
            "-N" 
        ]
        self.ssh_port_forwarding_process = subprocess.Popen(cmd)

    def stop_port_forwarding(self):
        if self.ssh_port_forwarding_process and self.ssh_port_forwarding_process.poll() is None:
            self.ssh_port_forwarding_process.terminate()
            self.ssh_port_forwarding_process.wait(timeout=5)
            self.ssh_port_forwarding_process = None
            print("Tunnel closed")
        else:
            print("Tunnel was not running")

    def close(self):
        self.disconnect()
        self.stop_port_forwarding()


class SSHConnectionSettings(QWidget):
    def __init__(self, ssh_client: SSHConnectionClient, parent=None):
        super().__init__(parent)
        self.ssh_client = ssh_client

        self.init_ui()

    def init_ui(self):
        # --- Input fields ---
        self.host_input = QLineEdit()
        self.host_input.setStyleSheet(f"border: 1px solid {BORDER};")
        self.port_input = QLineEdit()
        self.port_input.setStyleSheet(f"border: 1px solid {BORDER};")
        self.port_input.setText("22")  # Default SSH port
        self.username_input = QLineEdit()
        self.username_input.setStyleSheet(f"border: 1px solid {BORDER};")

        ssh_connection_label = QLabel("SSH connection")
        ssh_connection_form_layout = QFormLayout()
        ssh_connection_form_layout.addRow("IP:", self.host_input)
        ssh_connection_form_layout.addRow("Port:", self.port_input)
        ssh_connection_form_layout.addRow("Username:", self.username_input)
        ssh_connection_form_layout.addRow("Password:", QLabel("Please set up a SSH key for the connection"))

        port_forwarding_label = QLabel("Port forwarding", alignment=Qt.AlignmentFlag.AlignCenter)
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
        self.connect_button = QPushButton("Connect")
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.connect_button)

        # --- Layout ---
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(ssh_connection_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(ssh_connection_form_layout)
        layout.addWidget(port_forwarding_label)
        layout.addLayout(port_forwarding_form_layout)
        layout.addLayout(button_layout)

        # --- Connections ---
        self.connect_button.clicked.connect(self.try_connect)

    def try_connect(self):
        host = self.host_input.text().strip()
        port = int(self.port_input.text().strip() or 22)
        username = self.username_input.text().strip()

        local_port = int(self.local_port_input.text().strip())
        remote_port = int(self.remote_port_input.text().strip())
        remote_host = self.remote_host_input.text()

        success, exception = self.ssh_client.connect(username, host, port)
        print("success: ", success)
        if success:
            self.ssh_client.start_port_forwarding(local_port, remote_host, remote_port, username, host)
            QMessageBox.information(self, "Success", f"Connected to {host}.")
        else:
            QMessageBox.critical(self, "Connection Failed", f"SSH connection failed: {exception}")

