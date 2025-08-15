from .styles import get_task_label_style, get_task_widget_style, get_task_widget_style_clicked
from Server.Backend.types import Task
from PySide6.QtWidgets import (QFrame, QHBoxLayout, QWidget, QLabel, QSizePolicy,
QVBoxLayout)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QMouseEvent, QColor, QPainter


class StatusLight(QWidget):
    def __init__(self, size=20, status="off", parent=None):
        super().__init__(parent)
        self._size = size
        self._status = status
        self._colors = {
            "off": QColor("#999"),      # gray
            "on": QColor("#0f0"),       # green
            "warning": QColor("#ff0"),  # yellow
            "error": QColor("#f00"),    # red
        }
        self.setMinimumSize(size, size)

    def sizeHint(self):
        return QSize(self._size, self._size)

    def set_status(self, status):
        if status in self._colors:
            self._status = status
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._colors[self._status])
        diameter = min(self.width(), self.height())
        painter.drawEllipse(0, 0, diameter, diameter)


class TaskViewObject(QWidget):
    # drag_signal = Signal(int, int)

    def __init__(self, task: Task) -> None:
        super().__init__()
        self.task = task
        self.is_selected = False

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.frame = QWidget()
        self.frame.setStyleSheet(get_task_widget_style())
        layout = QHBoxLayout(self.frame)

        
        name_label = QLabel(f"{self.task.name}")
        name_label.setStyleSheet("background-color: transparent; border: none;")

        id_label = QLabel(f"{self.task.task_id}")
        id_label.setStyleSheet("background-color: transparent; border: none;")

        status_widget = StatusLight(11)

        layout.addWidget(name_label)
        layout.addWidget(id_label)
        layout.addStretch()
        layout.addWidget(status_widget)

        main_layout.addWidget(self.frame)

    def mousePressEvent(self, event):
        # this would be better over signals to the task_viewer!
        if event.button() == Qt.MouseButton.LeftButton:
            if self.is_selected:
                self.frame.setStyleSheet(get_task_widget_style_clicked())
            else:
                self.frame.setStyleSheet(get_task_widget_style())
            self.is_selected = not self.is_selected
        super().mousePressEvent(event)

    # def mousePressEvent(self, event: QMouseEvent):
    #     if event.button() == Qt.MouseButton.LeftButton:
    #         self.drag_start_pos = event.globalPosition().toPoint()
    #
    # def mouseMoveEvent(self, event: QMouseEvent):
    #     if event.buttons() & Qt.MouseButton.LeftButton and self.drag_start_pos:
    #         diff = event.globalPosition().toPoint() - self.drag_start_pos
    #         self.move(self.pos() + diff)
    #         self.drag_start_pos = event.globalPosition().toPoint()
    #
    # def mouseReleaseEvent(self, event: QMouseEvent):
    #     self.drag_start_pos = None
