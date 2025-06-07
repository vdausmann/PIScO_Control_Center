from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QScrollArea,
    QApplication,
    QMessageBox,
    QTreeWidget,
    QTreeWidgetItem,
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QLabel,
)
from PySide6.QtCore import Qt
import sys
from .task import TaskObject, PopUpTaskSettings
from .helper import popUpTextEntry, TreeItemWidget
from .module import PopUpModuleSelection, Module, load_modules_from_file


class PIScOControlCenter(QMainWindow):
    def __init__(self, config):
        self.app = QApplication(sys.argv)
        print(config)

        super().__init__()
        self.setWindowTitle("Dynamic Object Adder")
        self.setMinimumSize(600, 400)
        self.resize(1080, 720)

        # Central widget and layout
        central_widget = QWidget()
        self.main_layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Button to add new object
        self.add_button = QPushButton("Add Task")
        self.add_button.clicked.connect(self.add_object)
        self.main_layout.addWidget(self.add_button)

        # Scroll area to hold the objects
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
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

        self.tasks = {}

        self.tree = QTreeWidget(self)
        self.tree.setHeaderHidden(True)
        self.tree.setAllColumnsShowFocus(True)
        self.tree.setSelectionBehavior(QTreeWidget.SelectRows)
        self.tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self.object_layout.addWidget(self.tree)

        # test:
        print(load_modules_from_file("modules.cfg"))
        task = TaskObject("test", {"TestModule": True}, self)
        # self.tree.addTopLevelItem(task)
        frame = QFrame()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        label = QLabel(task.name)
        delete_button = QPushButton("Delete")
        delete_button.setStyleSheet("QPushButton { color: red; border: none; }")
        delete_button.clicked.connect(lambda: self.delete_task(task.name))
        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(delete_button)
        # self.object_layout.addWidget(task, alignment=Qt.AlignmentFlag.AlignCenter)
        self.tasks[task.name] = task
        self.tree.setItemWidget(task, 0, frame)

        self.show()
        sys.exit(self.app.exec())

    def on_item_click(self, item, column):
        if item.childCount() > 0:
            item.setExpanded(not item.isExpanded())
        print(f"Clicked on: {item.text(0)}")

    def add_object(self):
        ret, name = popUpTextEntry(self, "Adding a Task", "Enter Name of Task:")
        if not ret or not name:
            return
        if name in self.tasks:
            QMessageBox.warning(None, "Warning", "Tasks need unique names!")
            return

        dialog = PopUpModuleSelection(["Module 1", "Module 2"])
        if not dialog.exec():
            return

        selected = dialog.get_selected()
        modules = [Module(m) for m in dialog.get_selected() if dialog.get_selected()[m]]
        for module in modules:
            PopUpTaskSettings(module, self).exec()

        task = TaskObject(name, dialog.get_selected(), self)
        self.object_layout.addWidget(task, alignment=Qt.AlignmentFlag.AlignCenter)
        self.tasks[task.name] = task

    def add_task(self, name, modules): ...

    def delete_task(self, name: str):
        self.tree.takeTopLevelItem(self.tree.indexOfTopLevelItem(self.tasks[name]))
