from PySide6.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QMenu,
    QWidget,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from .helper import TreeNode
from .module_vis import ModuleObject
from App.Backend.task import Task


class TaskObject(TreeNode):
    def __init__(self, task: Task, tree):
        super().__init__()
        self.task = task
        self.tree = tree

        self.init_ui()

    def init_ui(self):
        node = QLabel(self.task.name)
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        node.setFont(font)
        self.add_object([node])
        for module in self.task.modules:
            module_object = ModuleObject(module)
            self.add_child(module_object)
        # self.status_label = QLabel(text_idle())
        # self.tree.setItemWidget(self, 1, self.status_label)

    def on_right_click(self, event):
        menu = TaskObjectMenu(self, self.tree)
        item_rect = self.header_container.rect()
        action = menu.exec(self.mapToGlobal(item_rect.bottomLeft()))
        menu.run_action(action)


class TaskObjectMenu(QMenu):
    def __init__(self, task_object: TaskObject, tree):
        super().__init__()
        self.task_object = task_object
        self.tree = tree
        self.action_info = self.addAction("Info")
        self.action_move = self.addAction(
            "Deactivate" if self.task_object.task.active else "Activate"
        )
        self.action_delete = self.addAction("Delete Task")

    def run_action(self, action):
        if action == self.action_info:
            # QMessageBox.information(self, "Info", f"You clicked: {item.text(0)}")
            ...
        elif action == self.action_move:
            self.tree.app.move_task(self.task_object, self.tree)
        elif action == self.action_delete:
            self.tree.delete_task(self.task_object)
            self.task_object.deleteLater()


class TaskTree(QWidget):
    def __init__(self, callback, app):
        super().__init__()
        self.tasks: list[TaskObject] = []
        self.callback = callback
        self.app = app

        self.tree_layout = QVBoxLayout(self)
        self.tree_layout.setSpacing(2)
        self.tree_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    def add_task_object(self, task: TaskObject):
        self.tree_layout.addWidget(task)
        task.tree = self
        self.tasks.append(task)

    def delete_task(self, task: TaskObject):
        self.tree_layout.removeWidget(task)
        self.tasks.remove(task)
        task.setParent(None)
