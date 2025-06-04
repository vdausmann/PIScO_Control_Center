from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt

class ClickableLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.container = parent

    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            self.container.print_text()
        super().mousePressEvent(ev)  # Pass the event to the base class

