from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListView, QLabel, QLineEdit, QDialog, QFormLayout,
    QMessageBox, QScrollArea, QSizePolicy, QSpacerItem, QComboBox
)

class PIScOControlCenter(QMainWindow):
    """Main application window for the PISCO-Controller."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Scientific Device Controller")
        self.setGeometry(100, 100, 1000, 700) # Initial window size

        # Connect application about to quit signal for state saving
        QApplication.instance().aboutToQuit.connect(self._save_app_state)

    def _save_app_state(self):
        """Called when the application is about to quit or when the state is manually saved to save the state."""
        ...
