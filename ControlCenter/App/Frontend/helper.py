from PySide6.QtWidgets import (
    QInputDialog,
    QWidget,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QMenu,
    QVBoxLayout,
    QLabel,
    QFrame,
    QGraphicsDropShadowEffect,
)
from PySide6.QtGui import QMouseEvent, QAction, QPalette, QColor, QPainter
from PySide6.QtCore import Qt, QPoint, Signal, QTimer, QPropertyAnimation, QSize

from collections.abc import Callable


def warning(text: str):
    QMessageBox.warning(None, "Warning", text)


def popUpTextEntry(parent: QWidget, title: str, label: str) -> tuple[bool, str]:
    text, ret = QInputDialog.getText(parent, title, label)
    return ret, text


class ScrollablePopUp(QDialog):
    def __init__(
        self, window_width=200, window_height=400, row_height=30, padding=2, parent=None
    ):
        super().__init__(parent)
        self.row_height = row_height
        self.window_height = window_height
        self.window_width = window_width
        self.padding = padding
        self.setFixedSize(self.window_width, self.window_height)

    def add_rows(
        self,
        rows: list[tuple[str, QHBoxLayout]],
        on_click: Callable[[QMouseEvent, str], None] = lambda event, i: None,
    ):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(self.padding)
        for id, row in rows:
            widget = QWidget()
            widget.setFixedSize(self.window_width, self.row_height)
            widget.setStyleSheet("background-color: #e0e0e0;")

            # row = QHBoxLayout(widget)
            # checkbox = QCheckBox()
            # label = QLabel(text=module)
            # row.addWidget(label, 1)
            # row.addWidget(checkbox)

            widget.setLayout(row)
            scroll_layout.addWidget(widget)
            widget.mousePressEvent = lambda event, i=id: on_click(event, i)

        for _ in range(
            len(rows), self.window_height // (self.row_height + self.padding) - 1
        ):
            widget = QWidget()
            # widget.setStyleSheet("background: transparent;")
            widget.setFixedSize(self.window_width, self.row_height)
            scroll_layout.addWidget(widget)

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        button_row = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_row.addStretch()
        button_row.addWidget(ok_button)
        button_row.addWidget(cancel_button)
        layout.addLayout(button_row)


class DropdownSettings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.button = QPushButton("...")
        self.button.setFixedSize(24, 24)
        self.button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button.setStyleSheet("""
            QPushButton {
                border: 1px solid #888;
                background-color: #dcdcdc;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton::menu-indicator {
                image: none;
            }
            QPushButton:hover {
                background-color: #c0c0c0;
            }
            QPushButton:pressed {
                background-color: #a8a8a8;
            }
        """)

        self.menu = QMenu(self)
        self.button.clicked.connect(self.show_menu)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.button)

    def show_menu(self):
        # Show menu right below the button
        self.menu.exec(self.button.mapToGlobal(QPoint(0, self.button.height())))

    def add_action_from_label(self, label: str, callback):
        action = QAction(label, self)
        action.triggered.connect(callback)
        self.menu.addAction(action)

    def add_action(self, action: QAction, callback):
        action.triggered.connect(callback)
        self.menu.addAction(action)


def color_text(text: str, color: str) -> str:
    return f'<span style="color:{color}; font-weight:bold;">{text}</span>'


# def task_status_text(status: str):
#     if status == "Idle":


def text_warning(text="Warning"):
    return color_text(text, "#f9a825")


def text_error(text="Error"):
    return color_text(text, "#c62828")


def text_running(text="Running"):
    return color_text(text, "#1565c0")


def text_inactive():
    return color_text("Inactive", "#555555")


def text_active():
    return color_text("Active", "#f9a825")


def text_finished():
    return color_text("Finished", "#2e7d32")


class TreeNode(QWidget):
    def __init__(self, is_leaf=True):
        super().__init__()
        self.is_leaf = is_leaf
        self.expanded = False

        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)
        main_layout.setSpacing(2)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.header_container = QWidget()
        self.header_container.setStyleSheet("""
            background-color: #e0e0e0;
        """)
        self.header_layout = QHBoxLayout(self.header_container)
        self.header_layout.setContentsMargins(0, 0, 0, 0)

        self.expand_icon = QLabel("▶" if not is_leaf else "  ")
        self.expand_icon.setFixedWidth(10)

        self.header_layout.addWidget(self.expand_icon)

        self.header_container.mousePressEvent = self.on_header_click

        main_layout.addWidget(self.header_container)

        self.children_container = QWidget()
        self.children_layout = QVBoxLayout(self.children_container)
        self.children_layout.setContentsMargins(20, 0, 0, 0)
        self.children_layout.setSpacing(2)
        self.children_container.setVisible(False)
        main_layout.addWidget(self.children_container)

    def add_object(self, objects: list[QFrame | QWidget]):
        for obj in objects:
            self.header_layout.addWidget(obj)

    def toggle(self):
        self.expanded = not self.expanded
        self.expand_icon.setText("▼" if self.expanded else "▶")
        self.children_container.setVisible(self.expanded)

    def on_header_click(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if not self.is_leaf:
                self.toggle()
        elif event.button() == Qt.MouseButton.RightButton:
            self.on_right_click(event)

    def on_right_click(self, event):
        return

    def add_child(self, child_node):
        self.children_layout.addWidget(child_node)
        self.is_leaf = False
        self.expand_icon.setText("▶")


class StartStopButton(QPushButton):
    started = Signal()
    stopped = Signal()

    def __init__(self, parent=None):
        super().__init__()
        self._is_running = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(40, 25)
        self.update_style()
        self.clicked.connect(self.toggle)

    def toggle(self):
        self._is_running = not self._is_running
        if self._is_running:
            self.started.emit()
        else:
            self.stopped.emit()
        self.update_style()

    def update_style(self):
        if self._is_running:
            # self.setText("⏸ ")  # Stop (pause)
            self.setText("Stop")  # Stop (pause)
            self.setStyleSheet("""
                QPushButton {
                    background-color: #c62828;
                    color: white;
                    font-size: 12px;
                    border: 1px solid #b71c1c;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #b71c1c;
                }
            """)
        else:
            # self.setText("▶")  # Start
            self.setText("Start")  # Start
            self.setStyleSheet("""
                QPushButton {
                    background-color: #2e7d32;
                    color: white;
                    font-size: 12px;
                    border: 1px solid #1b5e20;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1b5e20;
                }
            """)


class StatusIndicator(QLabel):
    def __init__(self, diameter=12, parent=None):
        super().__init__(parent)
        self.diameter = diameter
        self.setFixedSize(QSize(diameter, diameter))
        self.set_inactive()

    def set_running(self):
        self.color = QColor("yellow")
        self.update()

    def set_inactive(self):
        self.color = QColor("red")
        self.update()

    def set_finished(self):
        self.color = QColor("green")
        self.update()

    def set_color(self, color: QColor):
        if isinstance(color, str):
            color = QColor(color)
        self.setStyleSheet(f"""
            background-color: {color.name()};
            border-radius: {self.diameter // 2}px;
        """)

    def paintEvent(self, arg__1):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(self.color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, self.width(), self.height())
