from PySide6.QtWidgets import QFileDialog, QLabel, QPushButton, QHBoxLayout, QFrame, QWidget
from .clickable_label import ClickableLabel

class LabelPathComb(QFrame):
    selected_path: str = ""
    def __init__(self, label: str, window):
        super().__init__()

        self.window = window
        self.name = label

        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(0)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.label = ClickableLabel(label, self)
        self.path_select = QPushButton("+", self)
        self.path_select.clicked.connect(self.select_path)
        self.path_select.setFixedSize(20, 20)

        self.setFixedSize(150, 50)

        self.label.setFixedWidth(50)

        layout.addWidget(self.label)
        layout.addWidget(self.path_select)

        self.setLayout(layout)

    def select_path(self):
        self.selected_path = QFileDialog.getExistingDirectory()
        self.window.print("Selected path: " + self.selected_path)

    def print_text(self):
        self.window.print(f"{self.name}: " + self.selected_path)

    def get(self):
        return self.selected_path
