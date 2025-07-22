from PySide6.QtWidgets import (
        QLineEdit, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QSpacerItem,
        QPushButton, QScrollArea, QFormLayout, QDialog
)
from PySide6.QtCore import Qt
from .styles import *


class MetaDataEditor(QDialog):
    def __init__(self, meta_data: dict = {}, parent=None):
        super().__init__(parent)
        self.meta_data = meta_data
        self.setWindowTitle("Settings Editor")
        self.setModal(True)
        self.setFixedSize(300, 500)
        self.names_inputs = {}
        self.inputs = {}

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        scroll_area = QScrollArea()

        self.form_layout = QVBoxLayout()
        self.form_layout.setContentsMargins(2, 0, 2, 0) # No extra margins for internal layout
        self.form_layout.setSpacing(0)

        internal_label = QLabel("Meta Data")
        internal_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #555; padding: 2px; border: none;")
        self.form_layout.addWidget(internal_label)

        for name in self.meta_data:
            row = QHBoxLayout()
            label = QLabel(name)
            label.setStyleSheet("font-size: 12px;")
            label.setFixedSize(50, 20)
            input = QLineEdit(self.meta_data[name])
            self.inputs[name] = input
            input.setStyleSheet("font-size: 12px;")
            input.setFixedSize(150, 20)

            row.addWidget(label)
            row.addWidget(input)
            self.form_layout.addLayout(row)


        add_button = QPushButton("+")
        add_button.setFixedSize(20, 20)
        add_button.clicked.connect(self.add_metadata)
        self.form_layout.addWidget(add_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.form_layout.addStretch()

        scroll_area.setLayout(self.form_layout)
        main_layout.addWidget(scroll_area, 8)

        # button_row = QWidget()
        button_row_layout = QHBoxLayout()
        button_row_layout.setContentsMargins(0, 0, 0, 0)

        accept_button = QPushButton("Ok")
        accept_button.clicked.connect(self._accept)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        button_row_layout.addWidget(accept_button)
        button_row_layout.addWidget(cancel_button)


        main_layout.addLayout(button_row_layout, 1)

    def _accept(self):
        for input in self.inputs.values():
            input.input.update_setting()
        self.accept()

    def add_metadata(self):
        layout = QHBoxLayout()
        input = QLineEdit()
        # input.editingFinished.connect()

        idx = self.form_layout.count()
        self.form_layout.insertLayout(idx, layout)
