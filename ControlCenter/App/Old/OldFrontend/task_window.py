from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QSpacerItem, QScrollArea
)
from PySide6.QtCore import Qt, Signal, Slot
from typing import override
import json

from App.NewBackend.task import Task, TaskState
from .styles import *

class TaskVis(QWidget):
    clicked_signal = Signal(Task)

    def __init__(self, task: Task):
        super().__init__()
        self.task = task
        self.init_ui()
        self.is_clicked = False

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.task.name)
        self.label.setFixedHeight(20)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet(get_task_label_style())

        layout.addWidget(self.label)

    @override
    def mousePressEvent(self, event):
        self.clicked_signal.emit(self.task)

    def clicked(self):
        if self.is_clicked:
            self.is_clicked = False
            self.label.setStyleSheet(get_task_label_style())
        else:
            self.is_clicked = True
            self.label.setStyleSheet(get_task_label_style_clicked())


class TaskWindow(QScrollArea):
    """Visualization class of the task window. Shows a list of tasks. """
    

    selected_task_changed_signal = Signal(Task)
    def __init__(self, tasks: list[Task]):
        super().__init__()
        self.tasks = tasks
        self.finished_tasks: list[Task] = []
        self.unfinished_tasks: list[Task] = []
        self.objects = {}
        self.indices = {}
        self.selected_task = None
        self.init_ui()

    def init_ui(self):
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(
            # Qt.ScrollBarPolicy.ScrollBarAsNeeded
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn
        )
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"""
            QScrollArea {{
                    border: none;
                }}
        """)

        main_window = QWidget()        
        main_layout = QVBoxLayout(main_window)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addSpacerItem(QSpacerItem(100, 10))

        for task in self.tasks:
            if task.get_state() == TaskState.Finished:
                self.finished_tasks.append(task)
            else:
                self.unfinished_tasks.append(task)

        unfinished_task_seperator = QLabel("Unfinished Tasks:")
        unfinished_task_seperator.setStyleSheet("font-size: 18px; font-weight: bold; color: #555; padding: 2px; border: none;")
        main_layout.addWidget(unfinished_task_seperator)
        self.unfinished_task_layout = QVBoxLayout()

        # for task in self.unfinished_tasks:
        #     t = TaskVis(task)
        #     self.unfinished_task_layout.addWidget(t)
        #     t.clicked_signal.connect(self.task_clicked)
        #     self.objects[task] = t
        #     self.indices[task] = self.unfinished_task_layout.count() - 1
        #     task.task_state_changed_signal.connect(self.task_state_changed)
        #     task.task_delete_signal.connect(self.delete_task)

        main_layout.addLayout(self.unfinished_task_layout)
        main_layout.addSpacerItem(QSpacerItem(10, 20))
        finished_task_seperator = QLabel("Finished Tasks:")
        finished_task_seperator.setStyleSheet("font-size: 18px; font-weight: bold; color: #555; padding: 2px; border: none;")
        main_layout.addWidget(finished_task_seperator)
        self.finished_task_layout = QVBoxLayout()

        # for task in self.finished_tasks:
        #     t = TaskVis(task)
        #     self.finished_task_layout.addWidget(t)
        #     t.clicked_signal.connect(self.task_clicked)
        #     self.objects[task] = t
        #     self.indices[task] = self.finished_task_layout.count() - 1
        #     task.task_state_changed_signal.connect(self.task_state_changed)
        #     task.task_delete_signal.connect(self.delete_task)

        main_layout.addLayout(self.finished_task_layout)
        main_layout.addStretch()

        self.setWidget(main_window)

    @Slot()
    def delete_task_slot(self):
        task = self.sender()
        self.delete_task(task)

    def delete_task(self, task):
        idx = self.indices[task]
        if task in self.finished_tasks:
            for t in self.finished_tasks:
                if self.indices[t] > idx:
                    self.indices[t] -= 1
            self.finished_tasks.remove(task)
        elif task in self.unfinished_tasks:
            for t in self.unfinished_tasks:
                if self.indices[t] > idx:
                    self.indices[t] -= 1
            self.unfinished_tasks.remove(task)

        self.tasks.remove(task)
        task.task_state_changed_signal.disconnect(self.task_state_changed)
        task.task_delete_signal.disconnect(self.delete_task)
        self.objects[task].setParent(None)
        self.objects[task].deleteLater()
        self.objects.pop(task)
        self.selected_task = None
        self.selected_task_changed_signal.emit(self.selected_task)

    def add_task(self, task: Task):
        self.tasks.append(task)
        if task.get_state() == TaskState.Finished:
            self.finished_tasks.append(task)
            t = TaskVis(task)
            self.finished_task_layout.addWidget(t)
            t.clicked_signal.connect(self.task_clicked)
            self.objects[task] = t
            self.indices[task] = self.finished_task_layout.count() - 1
            task.task_state_changed_signal.connect(self.task_state_changed)
            task.task_delete_signal.connect(self.delete_task_slot)
        else:
            self.unfinished_tasks.append(task)
            t = TaskVis(task)
            self.unfinished_task_layout.addWidget(t)
            t.clicked_signal.connect(self.task_clicked)
            self.objects[task] = t
            self.indices[task] = self.unfinished_task_layout.count() - 1
            task.task_state_changed_signal.connect(self.task_state_changed)
            task.task_delete_signal.connect(self.delete_task_slot)

        # reset running state to idle
        if task.get_state() == TaskState.Running:
            task.set_state(TaskState.Idle)

    @Slot(Task)
    def task_clicked(self, task: Task):
        if self.selected_task is None:
            self.objects[task].clicked()
            self.selected_task = task
        elif self.selected_task == task:
            self.objects[task].clicked()
            self.selected_task = None
        elif self.selected_task is not None:
            self.objects[self.selected_task].clicked()
            self.objects[task].clicked()
            self.selected_task = task
        self.selected_task_changed_signal.emit(self.selected_task)

    @Slot(TaskState)
    def task_state_changed(self, state: TaskState):
        task = self.sender()
        # check if task was finished before:
        if task in self.unfinished_tasks and state != TaskState.Finished:
            return

        if task in self.finished_tasks:
            old_index = self.indices[task]
            item = self.finished_task_layout.takeAt(old_index)
            new_index = self.unfinished_task_layout.count() 
            self.unfinished_task_layout.insertItem(new_index, item)

            for t in self.finished_tasks:
                if self.indices[t] > old_index:
                    self.indices[t] -= 1

            self.finished_tasks.remove(task)
            self.unfinished_tasks.append(task)
            self.indices[task] = new_index

        elif state == TaskState.Finished:
            old_index = self.indices[task]
            item = self.unfinished_task_layout.takeAt(old_index)
            new_index = 0
            self.finished_task_layout.insertItem(new_index, item)

            for t in self.finished_tasks:
                self.indices[t] += 1
            for t in self.unfinished_tasks:
                if self.indices[t] > old_index:
                    self.indices[t] -= 1

            self.unfinished_tasks.remove(task)
            self.finished_tasks.append(task)
            self.indices[task] = new_index

        # for i in range(self.main_layout.count()):
        #     print(self.main_layout.itemAt(i))

    def save_state(self, state: dict):
        state["task_window"] = {}
        state["task_window"]["unfinished_tasks"] = {}
        for task in self.unfinished_tasks:
            state["task_window"]["unfinished_tasks"][task.name] = task.to_dict()

        state["task_window"]["finished_tasks"] = {}
        for task in self.finished_tasks:
            state["task_window"]["finished_tasks"][task.name] = task.to_dict()

    def load_state(self, state: dict):
        while self.tasks:
            task = self.tasks[0]
            self.delete_task(task)

        unfinished_tasks = list(state["task_window"]["unfinished_tasks"].values())
        for task in unfinished_tasks:
            self.add_task(Task.from_dict(task))

        finished_tasks = list(state["task_window"]["finished_tasks"].values())
        for task in finished_tasks:
            self.add_task(Task.from_dict(task))
