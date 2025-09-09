from PySide6 import QtSvg  # 👈 this makes sure SVG icons work
from PySide6.QtWidgets import QApplication, QPushButton
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
import sys

app = QApplication(sys.argv)

btn = QPushButton()
btn.setIcon(QIcon("/home/tim/Documents/Arbeit/Data/TestModule/0.jpg"))
btn.setIconSize(QSize(24, 24))   # must set explicitly
btn.setFixedSize(32, 32)         # keep square

icon = QIcon("/home/tim/Documents/Arbeit/Data/TestModule/0.jpg")
print("Loaded:", not icon.isNull())

btn.show()
sys.exit(app.exec())
