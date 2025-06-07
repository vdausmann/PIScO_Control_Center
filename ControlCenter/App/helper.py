from PySide6.QtWidgets import (QInputDialog, QWidget, QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QLabel, QPushButton,
QScrollArea, QMenu, QWidgetAction, QVBoxLayout)
from PySide6.QtGui import QMouseEvent, QAction, QIcon
from PySide6.QtCore import Qt, QPoint

from collections.abc import Callable


def popUpTextEntry(parent: QWidget, title: str, label: str) -> tuple[bool, str]:
    text, ret = QInputDialog.getText(parent, title, label)
    return ret, text

class ScrollablePopUp(QDialog):
    def __init__(self, window_width=200, window_height=400, row_height=30, padding=2, parent=None):
        super().__init__(parent)
        self.row_height = row_height
        self.window_height = window_height
        self.window_width = window_width
        self.padding = padding
        self.setFixedSize(self.window_width, self.window_height)


    def add_rows(self, rows: list[tuple[str, QHBoxLayout]], on_click: Callable[[QMouseEvent, str], None] = lambda event,
                 i: None):
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
            widget.setStyleSheet("background-color: #888;")

            # row = QHBoxLayout(widget)
            # checkbox = QCheckBox()
            # label = QLabel(text=module)
            # row.addWidget(label, 1)
            # row.addWidget(checkbox)
            
            widget.setLayout(row)
            scroll_layout.addWidget(widget)
            widget.mousePressEvent = lambda event, i=id: on_click(event, i)


        for _ in range(len(rows), self.window_height // (self.row_height + self.padding) - 1):
            widget = QWidget()
            widget.setStyleSheet("background: transparent;")
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
        self.button.setCursor(Qt.PointingHandCursor)
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


class TreeItemWidget(QWidget):
    def __init__(self, label, level=0, on_click: Callable[[QLabel], None]=lambda _: None, leaf_node:bool = False):
        super().__init__()
        self.level = level
        self.label = label
        self.on_click = on_click
        self.children_visible = False
        self.child_nodes = []

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        if leaf_node:
            self.header = QLabel(" " * 4 * level + label)
            self.header.setStyleSheet("""
                    border: none;
                    text-align: left;
                    padding: 4px;
                    font-weight: bold;
                    background-color: #f0f0f0;
            """)
            self.main_layout.addWidget(self.header)
        else:
            self.header = QPushButton(f"{' ' * (4 * level)}▶ {label}")
            self.header.setStyleSheet("""
                QPushButton {
                    border: none;
                    text-align: left;
                    padding: 4px;
                    font-weight: bold;
                    background-color: #f0f0f0;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)
            self.header.clicked.connect(self.toggle_children)
            if self.on_click:
                self.header.clicked.connect(lambda: self.on_click(self.label))

            self.main_layout.addWidget(self.header)

            self.child_container = QWidget()
            self.child_layout = QVBoxLayout(self.child_container)
            self.child_layout.setContentsMargins(0, 0, 0, 0)
            self.child_container.setVisible(False)
            self.main_layout.addWidget(self.child_container)


    def add_child(self, child_widget):
        self.child_nodes.append(child_widget)
        self.child_layout.addWidget(child_widget)

    def toggle_children(self):
        self.children_visible = not self.children_visible
        self.child_container.setVisible(self.children_visible)
        arrow = "▼" if self.children_visible else "▶"
        self.header.setText(f"{' ' * (4 * self.level)}{arrow} {self.label}")

