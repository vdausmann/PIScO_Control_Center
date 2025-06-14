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
from App.Backend.task import Task


class TaskObject(TreeNode):
    task_active_changed = Signal(bool)

    def __init__(self, task: Task, tree):
        super().__init__()
        self.task = task
        self.tree = tree
        self.running = False
        self.modules: list[ModuleObject] = []

        self.init_ui()

    def init_ui(self):
        self.label = QLabel(self.task.name)
        self.rename_input = QLineEdit()
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        self.label.setFont(font)
        self.add_object([self.label, self.rename_input])
        self.rename_input.hide()
        self.label.mouseDoubleClickEvent = lambda event: self.start_rename_task()
        self.rename_input.editingFinished.connect(self.finish_rename_task)
        # self.header_layout.addWidget(self.node)
        for module in self.task.modules:
            module_object = ModuleObject(module)
            self.modules.append(module_object)
            self.add_child(module_object)

        self.progress_label = QLabel("Progress: 1/4")
        self.header_layout.addWidget(
            self.progress_label, 1, alignment=Qt.AlignmentFlag.AlignCenter
        )

        self.status_label = QLabel()
        self.set_status()
        self.toggle_active(False)

        self.header_layout.addStretch()
        self.add_object([self.status_label])

    def add_module(self, module_object: ModuleObject):
        self.modules.append(module_object)
        self.add_child(module_object)

    def start_rename_task(self):
        self.label.hide()
        self.rename_input.setText(self.task.name)
        self.rename_input.show()
        self.rename_input.setFocus()
        self.rename_input.selectAll()

    def finish_rename_task(self):
        self.task.name = self.rename_input.text()
        self.label.setText(self.task.name)
        self.rename_input.hide()
        self.label.show()

    def set_status(self):
        if self.task.finished:
            self.status_label.setText(text_finished())
        elif not self.task.active:
            self.status_label.setText(text_inactive())
        elif self.running:
            self.status_label.setText(text_running())
        else:
            self.status_label.setText(text_active())

    def toggle_active(self, change_active: bool = True):
        if change_active:
            self.task.toggle_active()
            # self.task.active = not self.task.active
            # self.task_active_changed.emit(self.task.active)
        for module in self.modules:
            for setting in module.external_settings:
                setting.input.set_editable(not self.task.active)
            for setting in module.internal_settings:
                setting.input.set_editable(not self.task.active)
        self.set_status()

    def on_right_click(self, event):
        menu = TaskObjectMenu(self, self.tree)
        item_rect = self.header_container.rect()
        action = menu.exec(self.mapToGlobal(item_rect.bottomLeft()))
        menu.run_action(action)

    def set_finished(self):
        self.label.setStyleSheet("color: #2e7d32;")
        self.status_label.setText(text_finished())


class TaskObjectMenu(QMenu):
    def __init__(self, task_object: TaskObject, tree):
        super().__init__()
        self.task_object = task_object
        self.tree = tree
        self.action_info = self.addAction("Info")
        self.action_activate = self.addAction(
            "Deactivate" if self.task_object.task.active else "Activate"
        )
        self.action_add_module = self.addAction("Add module")
        self.action_duplicate = self.addAction("Duplicate")
        self.action_rename = self.addAction("Rename")
        self.action_delete = self.addAction("Delete")

        if self.task_object.task.active:
            self.action_rename.setEnabled(False)
            self.action_delete.setEnabled(False)
            self.action_add_module.setEnabled(False)

    def run_action(self, action):
        if action == self.action_info:
            QMessageBox.information(self, "Info", "Not implemented")
        elif action == self.action_activate:
            self.task_object.toggle_active()
        elif action == self.action_duplicate:
            task_copy = Task(
                self.task_object.task.name + " copy",
                [m.module for m in self.task_object.modules + []],
            )
            task_object_copy = TaskObject(task_copy, self.tree)
            self.tree.add_task_object(
                task_object_copy, self.tree.get_index(self.task_object) + 1
            )
        elif action == self.action_rename:
            self.task_object.start_rename_task()
        elif action == self.action_delete:
            self.tree.delete_task(self.task_object)
            self.task_object.deleteLater()
        elif action == self.action_add_module:
            popup = PopUpModuleSelection(
                exclude=[m.module for m in self.task_object.modules]
            )
            if popup.run():
                for module in popup.get_selected():
                    module_object = ModuleObject(module)
                    self.task_object.add_module(module_object)


class TaskTree(QWidget):
    def __init__(self, callback, app):
        super().__init__()
        self.tasks: list[TaskObject] = []
        self.callback = callback
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
