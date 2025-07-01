from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QScrollArea,
    QApplication,
    QMessageBox,
    QTreeWidget,
    QMenu,
    QFrame,
    QHBoxLayout,
    QLabel,
)
from .colors import *
from PySide6.QtCore import Qt, QPoint, QTimer
import sys
# from .task_vis import TaskObject, TaskObjectMenu, TaskTree
from .task import TaskObject, TaskTree
from .helper import popUpTextEntry, StartStopButton
from .notification import NotificationManager
from App.Backend import parser
from App.Backend.module import Module
from App.Backend.settings import Setting
from App.Backend.task import Task
from App.Backend.writer import write_current_state
from App.Backend.task_manager import TaskManager
from .module_vis import PopUpModuleSelection, ModuleObject
from .setting_vis import SettingObject
from .system_monitor import SystemMonitorCard


class PIScOControlCenter(QMainWindow):
    def __init__(self, config):
        self.app = QApplication(sys.argv)

        settings_dict = parser.get_modules_dict_from_file(config)
        self.task_manager = TaskManager(settings_dict["AppSettings"]["maxCores"])

        super().__init__()
        self.setWindowTitle("PIScOControlCenter")
        self.setMinimumSize(600, 400)
        self.resize(1080, 720)

        # Central widget and layout
        central_widget = QWidget()
        self.main_layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Scroll area to hold the objects
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.scroll_area.setStyleSheet(f"background-color: {BACKGROUND_COLOR1};")
        self.main_layout.addWidget(self.scroll_area, 3)

        # Task status region
        self.task_status_container = QFrame()
        self.task_status_container.setStyleSheet(f"border-color: {BODER_COLOR};")
        self.task_status_layout = QHBoxLayout()

        self.task_status_layout.addWidget(QLabel("Empty"), 2)

        self.system_monitor_widget = SystemMonitorCard()
        self.task_status_layout.addWidget(self.system_monitor_widget, 1)

        self.task_status_container.setLayout(self.task_status_layout)
        self.main_layout.addWidget(self.task_status_container, 1)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save)
        self.main_layout.addWidget(self.save_button)

        # Button to add new object
        self.add_task_button = QPushButton("Add Task")
        self.add_task_button.clicked.connect(self.add_new_task)
        self.main_layout.addWidget(self.add_task_button)


        # Container inside the scroll area
        self.object_container = QWidget()
        self.object_layout = QVBoxLayout()
        self.object_layout.setContentsMargins(0, 0, 0, 0)
        self.object_layout.setSpacing(0)
        self.object_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.object_container.setLayout(self.object_layout)
        self.scroll_area.setWidget(self.object_container)

        self.task_tree = TaskTree(self)
        self.object_layout.addWidget(self.task_tree)

        # load app state:
        try:
            tasks = parser.load_app_state("tmp/app_state.yaml")
            for task in tasks:
                self.add_task(task, self.tasks_tree)
        except Exception as e:
            print("Loading not possible", e)

    #     # # test:
    #     # modules = load_modules_from_file("modules.yaml")
    #     # task1 = Task("Test 1", [modules[0]])
    #     # self.add_task(task1, self.tasks_tree)
    #     # task2 = Task("Test 2", modules)
    #     # self.add_task(task2, self.tasks_tree)
    #     # task3 = Task("Test 3", modules, True)
    #     # self.add_task(task3, self.tasks_tree)
    #
    #     self.notifications_manager = NotificationManager(self)
    #
    #     self.autosave_timer = QTimer(self)
    #     self.autosave_timer.timeout.connect(self.save)
    #     self.autosave_timer.start(5 * 60 * 1000)

        self.show()
        sys.exit(self.app.exec())

    # def open_tree_menu(self, tree: QTreeWidget, point):
    #     item = tree.itemAt(point)
    #     if item:
    #         if type(item) is TaskObject:
    #             menu = TaskObjectMenu(item, tree)
    #         elif type(item) is ModuleObject:
    #             menu = TaskObjectMenu(item, tree)
    #         else:
    #             return
    #
    #         item_rect = tree.visualItemRect(item)
    #         action = menu.exec(tree.viewport().mapToGlobal(item_rect.bottomLeft()))
    #         menu.run_action(action)
    #
    # def add_new_task(self):
    #     task = Task("New Task", [])
    #     self.add_task(task, self.tasks_tree)

    def add_task(self, task: Task, tree: TaskTree):
        task_object = TaskObject(task, tree)
        tree.add_task_object(task_object)
        self.task_manager.add_task(task)

    def save(self):
        parser.write_current_state(
            [t.task for t in self.tasks_tree.tasks],
        )
        # self.notifications_manager.show_notification("Saved")
