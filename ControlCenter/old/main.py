from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QInputDialog, QSpacerItem
from PySide6.QtCore import Qt
from App import PIScOControlCenter


if __name__ == "__main__":
    PIScOControlCenter("./PIScO_Control_Center.json")
