from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QInputDialog
import sys


app = QApplication(sys.argv)

window = QMainWindow()
window.setWindowTitle("Test")

# button = QPushButton(window)
# button.setText("Button")

text = QInputDialog(window)
# text.setLabelText("Test")
s, ok = text.getText(window, "Test", "Test")
if ok and s:
    print(s)

# window.setCentralWidget(button)
# window.setCentralWidget(text) 

window.show()

sys.exit(app.exec())
