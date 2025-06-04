from PySide6.QtWidgets import QLineEdit, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QFrame
from .clickable_label import ClickableLabel

class LabelEntryComb(QFrame):

    text_entry: QLineEdit

    def __init__(self, label: str, window, app, value: str = ""):
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
        self.text_entry = QLineEdit()

        self.text_entry.setText(value)

        self.width = app.layout_settings["label_entry_comb_width"]
        self.height = app.layout_settings["label_entry_comb_height"]
        self.setFixedSize(self.width, self.height)

        self.label.setFixedWidth(app.layout_settings["label_entry_comb_label_width_percentage"] * self.width)
        self.text_entry.setFixedWidth((1 - app.layout_settings["label_entry_comb_label_width_percentage"]) * self.width)

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

