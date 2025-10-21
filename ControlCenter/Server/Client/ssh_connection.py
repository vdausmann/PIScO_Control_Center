import subprocess
import paramiko

class SSHConnectionClient:

    def __init__(self) -> None:
        self.ssh_client: paramiko.SSHClient | None = None
        self.ssh_port_forwarding_process: subprocess.Popen | None = None

    def connect(self, username: str, host: str, port: int = 22):
        # Already connected
        if self.ssh_client is not None:
            # QMessageBox.information(None, "Already connected", "Already connected via ssh.")
            return False, "Already connected"

        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh_client.connect(host, port=port, username=username, timeout=5)
            return True, None
        except Exception as e:
            return False, e

    def disconnect(self) -> bool:
        if self.ssh_client is not None:
            self.ssh_client.close()
            self.ssh_client = None
            return True
        return False

    def run_command(self, command: str) -> tuple[bool, str, str]:
        if self.ssh_client is None:
            # QMessageBox.warning(None, "Not connected", "Please connect first.")
            return False, "", ""
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        return True, output, error

    def start_port_forwarding(self, local_port: int, remote_host: str, remote_port: int,
                           username: str, host: str):
        """Forward local_port → remote_host:remote_port through the SSH tunnel."""
        if self.ssh_port_forwarding_process is not None:
            # QMessageBox.information(None, "Already connected", "Port forwarding process already running")
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

