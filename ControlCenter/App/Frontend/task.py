from PySide6.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QMenu,
    QWidget,
    QLineEdit,
    QMessageBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from .helper import TreeNode, text_inactive, text_active, text_finished, text_running
from .module_vis import ModuleObject, PopUpModuleSelection
from App.Backend.task import Task, TaskState
from App.Backend.task_manager import TaskManager


class TaskObject(TreeNode):

    def __init__(self, task: Task, tree):
        self.task = task
        self.tree = tree

        self.init_ui()

    def init_ui(self):
        # label with renaming:
        self.label = QLabel(self.task.name)
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        self.label.setFont(font)
        self.rename_input = QLineEdit()
        self.add_object([self.label, self.rename_input])
        self.rename_input.hide()
        self.label.mouseDoubleClickEvent = lambda event: self.rename_task(False)
        self.rename_input.editingFinished.connect(lambda: self.rename_task(True))

    def rename_task(self, finish: bool):
        if not finish:
            self.label.hide()
            self.rename_input.setText(self.task.name)
            self.rename_input.show()
            self.rename_input.setFocus()
            self.rename_input.selectAll()
        else:
            self.task.name = self.rename_input.text()
            self.label.setText(self.task.name)
            self.rename_input.hide()
            self.label.show()


class TaskTree(QWidget):
    def __init__(self, app):
        super().__init__()
        self.tasks: list[TaskObject] = []
        # self.callback = callback
        self.app = app

        self.tree_layout = QVBoxLayout(self)
        self.tree_layout.setSpacing(2)
        self.tree_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    def add_task_object(self, task_object: TaskObject, index=-1):
        idx = 0
        while idx < len(self.tasks):
            if self.tasks[idx].task.name == task_object.task.name:
                task_object.task.name += " copy"
                task_object.label.setText(task_object.task.name)
                idx = 0
            else:
                idx += 1

        self.tree_layout.insertWidget(index, task_object)
        task_object.tree = self
        self.tasks.append(task_object)

    def delete_task(self, task: TaskObject):
        self.tree_layout.removeWidget(task)
        self.tasks.remove(task)
        self.app.task_manager.remove_task(task.task)
        task.setParent(None)

    def get_index(self, task_object: TaskObject):
        idx = None
        for i in range(self.tree_layout.count()):
            if self.tree_layout.itemAt(i).widget() == task_object:
                idx = i
                break
        return idx
