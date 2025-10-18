from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QLabel
)
from PySide6.QtCore import Qt

class ServerViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        label = QLabel("<h2>Server viewer</h2>"
                       "<p>Not Implemented</p>")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addStretch(1) # Push content to top

        self.setStyleSheet("""
            QWidget#OtherPage {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 10px;
            }
            QLabel {
                color: #555;
                font-size: 16px;
            }
            h2 {
                color: #007bff;
            }
        """)
        self.setObjectName("OtherPage") # Set object name for styling

    def save_state(self, state: dict):
        ...

    def load_state(self, state: dict):
        ...
