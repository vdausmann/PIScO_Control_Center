from PySide6.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QMenu,
    QWidget,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from .helper import TreeNode, text_inactive, text_active
from .module_vis import ModuleObject
from App.Backend.task import Task


class TaskObject(TreeNode):
    def __init__(self, task: Task, tree):
        super().__init__()
        self.task = task
        self.tree = tree
        self.modules = []

        self.init_ui()

    def init_ui(self):
        self.node = QLabel(self.task.name)
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        self.node.setFont(font)
        self.add_object([self.node])
        # self.header_layout.addWidget(self.node)
        for module in self.task.modules:
            module_object = ModuleObject(module)
            self.modules.append(module_object)
            self.add_child(module_object)

        status = text_inactive() if not self.task.active else text_active()
        self.status_label = QLabel(status)
        self.toggle_active(False)

        self.header_layout.addStretch()
        self.add_object([self.status_label])

        if self.task.active:
            self.set_finished()

    def toggle_active(self, change_active: bool = True):
        if change_active:
            self.task.active = not self.task.active
        for module in self.modules:
            for setting in module.external_settings:
                setting.input.set_editable(not self.task.active)
            for setting in module.internal_settings:
                setting.input.set_editable(not self.task.active)
        status = text_inactive() if not self.task.active else text_active()
        self.status_label.setText(status)

    def on_right_click(self, event):
        menu = TaskObjectMenu(self, self.tree)
        item_rect = self.header_container.rect()
        action = menu.exec(self.mapToGlobal(item_rect.bottomLeft()))
        menu.run_action(action)

    def set_finished(self):
        self.node.setStyleSheet("color: #2e7d32;")


class TaskObjectMenu(QMenu):
    def __init__(self, task_object: TaskObject, tree):
        super().__init__()
        self.task_object = task_object
        self.tree = tree
        self.action_info = self.addAction("Info")
        self.action_activate = self.addAction(
            "Deactivate" if self.task_object.task.active else "Activate"
        )
        self.action_rename = self.addAction("Rename")
        self.action_delete = self.addAction("Delete")

    def run_action(self, action):
        if action == self.action_info:
            # QMessageBox.information(self, "Info", f"You clicked: {item.text(0)}")
            ...
        elif action == self.action_activate:
            self.task_object.toggle_active()
        elif action == self.action_rename:
            ...
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

    def add_task_object(self, task: TaskObject, index=-1):
        self.tree_layout.insertWidget(index, task)
        task.tree = self
        self.tasks.append(task)

    def delete_task(self, task: TaskObject):
        self.tree_layout.removeWidget(task)
        self.tasks.remove(task)
        task.setParent(None)
