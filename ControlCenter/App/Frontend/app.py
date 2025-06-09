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
from PySide6.QtCore import Qt, QPoint, QTimer
import sys
from .task_vis import TaskObject, TaskObjectMenu, TaskTree
from .helper import popUpTextEntry, StartStopButton, PopupNotification
from App.Backend.module import Module
from App.Backend.settings import Setting
from App.Backend.task import Task
from App.Backend.parser import load_modules_from_file, load_app_state
from App.Backend.writer import write_current_state
from .module_vis import PopUpModuleSelection, ModuleObject
from .setting_vis import SettingObject


class PIScOControlCenter(QMainWindow):
    def __init__(self, config):
        self.app = QApplication(sys.argv)
        print(config)

        super().__init__()
        self.setWindowTitle("Dynamic Object Adder")
        self.setMinimumSize(600, 400)
        self.resize(1080, 720)

        self.inactive_tasks_tree = TaskTree(self.open_tree_menu, self)
        self.active_tasks_tree = TaskTree(self.open_tree_menu, self)

        # Central widget and layout
        central_widget = QWidget()
        self.main_layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Button to add new object
        self.add_button = QPushButton("Save")
        self.add_button.clicked.connect(self.save)
        self.main_layout.addWidget(self.add_button)

        # Scroll area to hold the objects
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.scroll_area.setStyleSheet("background-color: #f8f9fb;")
        self.main_layout.addWidget(self.scroll_area)

        # Container inside the scroll area
        self.object_container = QWidget()
        self.object_layout = QVBoxLayout()
        self.object_layout.setContentsMargins(0, 0, 0, 0)
        self.object_layout.setSpacing(0)
        self.object_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.object_container.setLayout(self.object_layout)
        self.scroll_area.setWidget(self.object_container)

        inactive_tasks_label = QLabel("Inactive Tasks")
        self.object_layout.addWidget(
            inactive_tasks_label, alignment=Qt.AlignmentFlag.AlignCenter
        )
        self.object_layout.addWidget(self.inactive_tasks_tree, 1)

        active_tasks_frame = QFrame()
        active_tasks_layout = QHBoxLayout(active_tasks_frame)
        active_tasks_label = QLabel("Active Tasks")
        active_tasks_layout.addWidget(
            active_tasks_label, 1, alignment=Qt.AlignmentFlag.AlignCenter
        )
        active_tasks_button = StartStopButton()
        active_tasks_button.started.connect(self.run_tasks)
        # active_tasks_button.stopped.connect()
        active_tasks_layout.addWidget(active_tasks_button)
        self.object_layout.addWidget(active_tasks_frame)

        self.object_layout.addWidget(self.active_tasks_tree, 1)

        # load app state:
        try:
            inactive_tasks, active_tasks = load_app_state("tmp/app_state.yaml")
            for task in inactive_tasks:
                t = Task(task, inactive_tasks[task])
                self.add_task(t, self.inactive_tasks_tree)
            for task in active_tasks:
                t = Task(task, active_tasks[task])
                self.add_task(t, self.active_tasks_tree)
        except Exception as e:
            print("Loading not possible", e)

        # test:
        # modules = load_modules_from_file("modules.yaml")
        # task1 = Task("Test 1", [modules[0]])
        # self.add_task(task1, self.inactive_tasks_tree)
        # task2 = Task("Test 2", modules)
        # self.add_task(task2, self.inactive_tasks_tree)
        # task3 = Task("Test 3", modules, True)
        # self.add_task(task3, self.active_tasks_tree)

        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start(5 * 60 * 1000)
        self.autosave()

        self.show()
        sys.exit(self.app.exec())

    def open_tree_menu(self, tree: QTreeWidget, point):
        item = tree.itemAt(point)
        if item:
            if type(item) is TaskObject:
                menu = TaskObjectMenu(item, tree)
            elif type(item) is ModuleObject:
                menu = TaskObjectMenu(item, tree)
            else:
                return

            item_rect = tree.visualItemRect(item)
            action = menu.exec(tree.viewport().mapToGlobal(item_rect.bottomLeft()))
            menu.run_action(action)

    def add_task(self, task: Task, tree: TaskTree):
        task_object = TaskObject(task, tree)
        tree.add_task_object(task_object)

    def move_task(self, task_object: TaskObject, origin: TaskTree):
        origin.delete_task(task_object)
        task_object.task.active = not task_object.task.active
        if task_object.task.active:
            self.active_tasks_tree.add_task_object(task_object)
        else:
            self.inactive_tasks_tree.add_task_object(task_object)

    def run_tasks(self):
        for task_object in self.active_tasks_tree.tasks:
            print(task_object.task.name)

    def save(self):
        write_current_state(
            [t.task for t in self.inactive_tasks_tree.tasks],
            [t.task for t in self.active_tasks_tree.tasks],
        )

    def autosave(self):
        print("saved")
        self.save()
        PopupNotification(self, "Autosaved")
