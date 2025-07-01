import sys
import psutil
from PySide6.QtWidgets import (
    QApplication, QSpacerItem, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont


class StatRow(QWidget):
    def __init__(self, label: str):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(4)

        self.label = QLabel(label)
        self.label.setFont(QFont("Arial", 9))
        self.label.setAlignment(Qt.AlignLeft)

        self.value = QLabel("...")
        self.value.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.value.setAlignment(Qt.AlignRight)

        layout.addWidget(self.label)
        layout.addWidget(self.value)

    def set_value(self, text: str):
        self.value.setText(text)


class SystemMonitorCard(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QWidget#Card {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
        """)
        self.setObjectName("Card")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        # main_layout.setSpacing(6)

        self.cpu_row = StatRow("CPU Usage")
        self.mem_row = StatRow("Memory")
        self.disk_rows = {}

        main_layout.addWidget(self.cpu_row)
        main_layout.addWidget(self.mem_row)
        self.disk_container = QVBoxLayout()
        main_layout.addLayout(self.disk_container)
        main_layout.addStretch()

        self.update_stats()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(500)

    def update_stats(self):
        cpu_percent = psutil.cpu_percent()
        self.cpu_row.set_value(f"{cpu_percent:.0f} %")

        mem = psutil.virtual_memory()
        mem_used = self.format_size(mem.used)
        mem_total = self.format_size(mem.total)
        self.mem_row.set_value(f"{mem_used} / {mem_total}")

        seen = set()
        for part in psutil.disk_partitions():
            if part.device in seen or not part.mountpoint.startswith("/") or part.mountpoint == "/boot":
                continue
            seen.add(part.device)
            try:
                usage = psutil.disk_usage(part.mountpoint)
                label = f"{part.mountpoint}"
                used = self.format_size(usage.used)
                total = self.format_size(usage.total)
                val = f"{used} / {total}"

                if part.mountpoint not in self.disk_rows:
                    row = StatRow(f"Disk {label}")
                    self.disk_rows[part.mountpoint] = row
                    self.disk_container.addWidget(row)
                self.disk_rows[part.mountpoint].set_value(val)

            except PermissionError:
                continue

    @staticmethod
    def format_size(bytes_val):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    layout = QVBoxLayout(window)
    layout.setAlignment(Qt.AlignTop)
    layout.setContentsMargins(20, 20, 20, 20)

    monitor = SystemMonitorCard()
    monitor.setFixedWidth(250)
    layout.addWidget(monitor)

    window.setWindowTitle("System Monitor Card")
    window.show()
    sys.exit(app.exec())

