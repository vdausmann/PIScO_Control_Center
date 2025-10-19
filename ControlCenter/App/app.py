import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListView, QLabel, QLineEdit, QDialog, QFormLayout,
    QMessageBox, QScrollArea, QSizePolicy, QSpacerItem, QComboBox, QFrame, QMenu,
    QToolBar, QStackedWidget, QStackedLayout
)
from PySide6.QtCore import QSize, Slot, Qt
from PySide6.QtGui import QIcon, QAction

from .TaskViewerPane import TaskViewerPane
from .CallibrationPane import CallibrationViewer
from .ProfileViewerPane import ProfileViewer
from .HDF5ViewerPane import HDF5Viewer
from .ServerPane import ServerViewer
from .Resources.styles import COLORS
from .ServerPane.server_client import ServerClient
# from .TaskViewerPane.module_editor import CreateNewModule, EditModule

class PIScOControlCenter(QMainWindow):
    """Main application window for the PISCO-Controller."""

    def __init__(self):
        self.app = QApplication(sys.argv)
        super().__init__()
        self.setScreen(self.app.screens()[0])


        self.setWindowTitle("PISCO-Controller")
        w = 1920
        h = 1080
        self.setMinimumSize(w, h)
        self.setGeometry((1920 - w) // 2, (1080 - h) // 2, w, h) # Initial window size


        # self.setStyleSheet(get_main_window_style())
        with open("App/Resources/style.qss", "r") as f:
            style = f.read()

        for key in COLORS:
            style = style.replace(key, COLORS[key])
        self.app.setStyleSheet(style)
        # print(style)

        self.client = ServerClient()

        self.init_ui()

        # Connect application about to quit signal for state saving
        self.app.aboutToQuit.connect(self._quit)
        # self.move(self.screen().geometry().topLeft())

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
        toolbar_frame.setObjectName("Toolbar")
        toolbar_frame.setStyleSheet("border-top: none;")
        button_size = 40
        toolbar_frame.setFixedWidth(button_size + 4)
        toolbar_layout = QVBoxLayout()
        toolbar_layout.setContentsMargins(0, 0, 0, 0)

        b1 = QPushButton("")
        b1.clicked.connect(lambda: self._show_page(0))
        b1.setIcon(QIcon("App/Resources/Icons/task_50dp_E3E3E3_FILL0_wght400_GRAD0_opsz48.png"))
        b1.setIconSize(QSize(24, 24))
        b1.setFixedWidth(button_size)
        b1.setFixedHeight(button_size)

        b2 = QPushButton("")
        b2.clicked.connect(lambda: self._show_page(1))
        b2.setIcon(QIcon("App/Resources/Icons/camera_50dp_E3E3E3_FILL0_wght400_GRAD0_opsz48.png"))
        b2.setIconSize(QSize(24, 24))
        b2.setFixedWidth(button_size)
        b2.setFixedHeight(button_size)

        b3 = QPushButton("")
        b3.clicked.connect(lambda: self._show_page(2))
        b3.setIcon(QIcon("App/Resources/Icons/chart_data_50dp_E3E3E3_FILL0_wght400_GRAD0_opsz48.png"))
        b3.setIconSize(QSize(24, 24))
        b3.setFixedWidth(button_size)
        b3.setFixedHeight(button_size)

        b4 = QPushButton("HDF5")
        b4.clicked.connect(lambda: self._show_page(3))
        b4.setStyleSheet("font-size: 10px; padding: 0px;")
        b4.setFixedWidth(button_size)
        b4.setFixedHeight(button_size)

        b5 = QPushButton("")
        b5.clicked.connect(lambda: self._show_page(4))
        b5.setIcon(QIcon("App/Resources/Icons/host_50dp_E3E3E3_FILL0_wght400_GRAD0_opsz48.png"))
        b5.setIconSize(QSize(24, 24))
        b5.setFixedWidth(button_size)
        b5.setFixedHeight(button_size)

        toolbar_layout.addSpacerItem(QSpacerItem(40, 10))
        toolbar_layout.addWidget(b1, alignment=Qt.AlignmentFlag.AlignCenter)
        toolbar_layout.addWidget(b2, alignment=Qt.AlignmentFlag.AlignCenter)
        toolbar_layout.addWidget(b3, alignment=Qt.AlignmentFlag.AlignCenter)
        toolbar_layout.addWidget(b4, alignment=Qt.AlignmentFlag.AlignCenter)
        toolbar_layout.addWidget(b5, alignment=Qt.AlignmentFlag.AlignCenter)
        toolbar_layout.addStretch()

        toolbar_frame.setLayout(toolbar_layout)

        main_layout.addWidget(toolbar_frame)

        self.stacked_widget = QStackedWidget() 

        self.task_viewer = TaskViewerPane()

        # task_pane = QWidget()
        # task_pane_layout = QHBoxLayout(task_pane)
        # task_pane_layout.setContentsMargins(0, 0, 0, 0)
        # task_pane_layout.setSpacing(0)
        # task_window = TaskWindow([])
        # # task_window.add_task(get_test_task("Task 1"))
        # # task_window.add_task(get_test_task("Task 2", True))
        # task_pane_layout.addWidget(task_window, 8)
        # viewer_pane = TaskViewer(task_window)
        # task_pane_layout.addWidget(viewer_pane, 4)
        # task_pane_layout.addStretch()
        # self.panes.append(task_window)
        #
        self.callibration_viewer = CallibrationViewer()
        # self.panes.append(callibration_pane)
        #
        #
        self.profile_viewer = ProfileViewer()
        # self.panes.append(profile_viewer)
        #

        self.hdf5_viewer = HDF5Viewer()
        self.server_viewer = ServerViewer(self.client)


        self.stacked_widget.addWidget(self.task_viewer)
        self.stacked_widget.addWidget(self.callibration_viewer)
        self.stacked_widget.addWidget(self.profile_viewer)
        self.stacked_widget.addWidget(self.hdf5_viewer)
        self.stacked_widget.addWidget(self.server_viewer)
        main_layout.addWidget(self.stacked_widget, 1)

    def add_menubar(self):
        menu = self.menuBar()

        file_menu = menu.addMenu("&File")
        save_state_action = QAction(QIcon.fromTheme("document-save", QIcon()), "&Save State", self)
        save_state_action.setToolTip("Save the current application state to a file")
        # save_state_action.setShortcut(Qt.CTRL | Qt.Key.Key_S)
        # save_state_action.triggered.connect(self._save_app_state)
        file_menu.addAction(save_state_action)
        file_menu.addSeparator()
        load_state_action = QAction(QIcon.fromTheme("document-load", QIcon()), "&Load State", self)
        load_state_action.setToolTip("Load application state from a file")
        # load_state_action.setShortcut(Qt.CTRL | Qt.Key.Key_L)
        file_menu.addAction(load_state_action)
        file_menu.addSeparator()

        modules_menu = menu.addMenu("&Modules")
        create_new_module = QAction("&Create new module", self)
        create_new_module.setToolTip("Create new module")
        # create_new_module.triggered.connect(self._create_new_module)
        modules_menu.addAction(create_new_module)
        modules_menu.addSeparator()
        
        edit_module = QAction("&Edit existing module", self)
        edit_module.setToolTip("Edit existing module")
        # edit_module.triggered.connect(self._edit_module)
        modules_menu.addAction(edit_module)
        modules_menu.addSeparator()



    @Slot(int)
    def _show_page(self, index: int):
        """Switches the currently visible page in the stacked widget."""
        self.stacked_widget.setCurrentIndex(index)

    def _quit(self):
        self.task_viewer.client.disconnect_from_server()
        self.client.close()




    # @Slot()
    # def _create_new_module(self):
    #     dialog = CreateNewModule()
    #     dialog.exec()
    #
    # @Slot()
    # def _edit_module(self):
    #     dialog = EditModule()
    #     dialog.exec()
    #     selected_module = dialog.get_selected()
    #
    #     print(selected_module)
    #     dialog = CreateNewModule(selected_module)
    #     dialog.exec()
