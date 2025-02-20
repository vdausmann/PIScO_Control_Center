from PySide6.QtWidgets import QLineEdit, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QFrame
from .clickable_label import ClickableLabel

class LabelEntryComb(QFrame):

    text_entry: QLineEdit

    def __init__(self, label: str, window, value: str = ""):
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
        self.text_entry = QLineEdit()

        self.text_entry.setText(value)
        # self.setFixedSize(150, 50)

        self.label.setFixedWidth(70)
        self.text_entry.setFixedWidth(70)

        layout.addWidget(self.label)
        layout.addWidget(self.text_entry)

        self.setLayout(layout)

    def get(self):
        return self.text_entry.text()

    def print_text(self):
        if self.get() == "":
            self.window.print(f"{self.name}: Not set" )
        else:
            self.window.print(f"{self.name}: " + self.get())

