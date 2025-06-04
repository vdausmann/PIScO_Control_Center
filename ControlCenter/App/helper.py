from PySide6.QtWidgets import (QInputDialog, QWidget, QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QLabel, QPushButton,
QScrollArea)


def popUpTextEntry(parent: QWidget, title: str, label: str) -> tuple[bool, str]:
    text, ret = QInputDialog.getText(parent, title, label)
    return ret, text

