from PySide6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QPushButton, QScrollArea, QApplication, QMessageBox, QTreeWidget,
        QTreeWidgetItem, QAbstractItemView
        )
from PySide6.QtCore import Qt
import sys
from .task import TaskObject, PopUpTaskSettings
from .helper import popUpTextEntry, TreeItemWidget
from .module import PopUpModuleSelection, Module

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

        # task1 = TreeItemWidget("Task 1", 0)
        # module1_1 = TreeItemWidget("Module 1", 1)
        # module1_2 = TreeItemWidget("Module 2", 1)
        # setting1_1 = TreeItemWidget("Setting 1", 2, leaf_node=True)
        # module1_1.add_child(setting1_1)
        # task1.add_child(module1_1)
        # task1.add_child(module1_2)
        #
        # task2 = TreeItemWidget("Task 2", 0)
        # module2_1 = TreeItemWidget("Module 1", 1)
        # module2_2 = TreeItemWidget("Module 2", 1)
        # task2.add_child(module2_1)
        # task2.add_child(module2_2)
        # self.object_layout.addWidget(task1)
        # self.object_layout.addWidget(task2)
        # self.object_layout.addStretch()

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setAllColumnsShowFocus(True)
        self.tree.setSelectionBehavior(QTreeWidget.SelectRows)
        self.tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tree.itemClicked.connect(self.on_item_click)

        self.object_layout.addWidget(self.tree)

        # Example data
        task1 = QTreeWidgetItem(["Task 1"])
        module1 = QTreeWidgetItem(["Module A"])
        module2 = QTreeWidgetItem(["Module B"])
        task1.addChildren([module1, module2])

        task2 = QTreeWidgetItem(["Task 2"])
        module3 = QTreeWidgetItem(["Module C"])
        setting1 = QTreeWidgetItem(["Setting 1"])
        setting2 = QTreeWidgetItem(["Setting 2"])
        module3.addChildren([setting1, setting2])
        task2.addChild(module3)

        self.tree.addTopLevelItems([task1, task2])

        # test:
        # task = TaskObject("test", {"TestModule": True}, self)
        # self.object_layout.addWidget(task, alignment=Qt.AlignmentFlag.AlignCenter)
        # self.tasks[task.name] = task

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

    def delete_task(self, name: str):
        self.object_layout.removeWidget(self.tasks[name])
        self.tasks[name].setParent(None)
        self.tasks[name].deleteLater()
        self.tasks.pop(name)
