from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QCheckBox
from .clickable_label import ClickableLabel

class LabelCheckboxComb(QFrame):
    def __init__(self, label: str, window, app, value: bool = False):
        super().__init__()
        self.window = window
        self.name = label
        self.app = app

        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(0)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.label = ClickableLabel(label, self)
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(value)

        # self.setFixedSize(150, 50)

        self.label.setFixedWidth(70)
        self.checkbox.setFixedWidth(70)

        layout.addWidget(self.label)
        layout.addWidget(self.checkbox)

        self.setLayout(layout)

    def get(self):
        return self.checkbox.isChecked()

    def print_text(self):
        self.window.print(f"{self.name}: {self.get()}" )

