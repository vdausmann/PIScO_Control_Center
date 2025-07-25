import sys
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListView, QLabel, QLineEdit, QDialog, QFormLayout,
    QMessageBox, QScrollArea, QSizePolicy, QSpacerItem, QComboBox, QFrame, QMenu,
    QToolBar, QStackedWidget, QStackedLayout
)
from PySide6.QtCore import QSize, Slot, Qt
from PySide6.QtGui import QIcon, QAction

from .task_window import TaskWindow
from .task_viewer import TaskViewer
from .callibration_window import CallibrationWindow
from .styles import get_main_window_style, get_toolbar_style
from .profile_viewer import ProfileViewer

from App.NewBackend.task import get_test_task

class PIScOControlCenter(QMainWindow):
    """Main application window for the PISCO-Controller."""

    def __init__(self):
        self.app = QApplication(sys.argv)
        super().__init__()
        self.setScreen(self.app.screens()[0])


        self.setWindowTitle("PISCO-Controller")
        self.setMinimumSize(800, 600)
        # self.setGeometry(0, 0, 1920, 1080) # Initial window size

        self.panes = []

        self.init_ui()

        # Connect application about to quit signal for state saving
        QApplication.instance().aboutToQuit.connect(self._save_app_state)

        self.move(self.screen().geometry().topLeft())

        # self.show()
        self.showMaximized()
        sys.exit(self.app.exec())

    def init_ui(self):
        self.add_menubar()
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        toolbar_frame = QWidget()
        toolbar_frame.setFixedWidth(44)
        toolbar_frame.setStyleSheet(get_toolbar_style())
        toolbar_layout = QVBoxLayout()
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        b1 = QPushButton("1")
        b1.clicked.connect(lambda: self._show_page(0))
        b1.setFixedWidth(30)
        b1.setFixedHeight(30)
        b2 = QPushButton("2")
        b2.clicked.connect(lambda: self._show_page(1))
        b2.setFixedWidth(30)
        b2.setFixedHeight(30)
        b3 = QPushButton("3")
        b3.clicked.connect(lambda: self._show_page(2))
        b3.setFixedWidth(30)
        b3.setFixedHeight(30)

        toolbar_layout.addSpacerItem(QSpacerItem(40, 10))
        toolbar_layout.addWidget(b1, alignment=Qt.AlignmentFlag.AlignCenter)
        toolbar_layout.addWidget(b2, alignment=Qt.AlignmentFlag.AlignCenter)
        toolbar_layout.addWidget(b3, alignment=Qt.AlignmentFlag.AlignCenter)
        toolbar_layout.addStretch()

        toolbar_frame.setLayout(toolbar_layout)

        main_layout.addWidget(toolbar_frame)

        self.stacked_widget = QStackedWidget() 

        task_pane = QWidget()
        task_pane_layout = QHBoxLayout(task_pane)
        task_pane_layout.setContentsMargins(0, 0, 0, 0)
        task_pane_layout.setSpacing(0)
        task_window = TaskWindow([])
        # task_window.add_task(get_test_task("Task 1"))
        # task_window.add_task(get_test_task("Task 2", True))
        task_pane_layout.addWidget(task_window, 8)
        viewer_pane = TaskViewer(task_window)
        task_pane_layout.addWidget(viewer_pane, 4)
        task_pane_layout.addStretch()
        self.panes.append(task_window)

        callibration_pane = CallibrationWindow()
        self.panes.append(callibration_pane)


        profile_viewer = ProfileViewer()
        self.panes.append(profile_viewer)

        self.stacked_widget.addWidget(task_pane)
        self.stacked_widget.addWidget(callibration_pane)
        self.stacked_widget.addWidget(profile_viewer)
        main_layout.addWidget(self.stacked_widget, 1)

        self.setStyleSheet(get_main_window_style())
        self._load_app_state()

    def add_menubar(self):
        menu = self.menuBar()

        file_menu = menu.addMenu("&File")
        save_state_action = QAction(QIcon.fromTheme("document-save", QIcon()), "&Save State", self)
        save_state_action.setToolTip("Save the current application state to a file")
        save_state_action.setShortcut(Qt.CTRL | Qt.Key.Key_S)
        save_state_action.triggered.connect(self._save_app_state)
        file_menu.addAction(save_state_action)
        file_menu.addSeparator()
        load_state_action = QAction(QIcon.fromTheme("document-load", QIcon()), "&Load State", self)
        load_state_action.setToolTip("Load application state from a file")
        load_state_action.setShortcut(Qt.CTRL | Qt.Key.Key_L)
        load_state_action.triggered.connect(self._load_app_state)
        file_menu.addAction(load_state_action)
        file_menu.addSeparator()


    def _save_app_state(self):
        """Called when the application is about to quit or when the state is manually saved to save the state."""
        state = {}
        for pane in self.panes:
            pane.save_state(state)
        with open(".app_state.json", "w") as f:
            json.dump(state, f, indent=2)

    def _load_app_state(self):
        with open(".app_state.json", "r") as f:
            state = json.load(f)

        for pane in self.panes:
            pane.load_state(state)

    @Slot(int)
    def _show_page(self, index: int):
        """Switches the currently visible page in the stacked widget."""
        self.stacked_widget.setCurrentIndex(index)
