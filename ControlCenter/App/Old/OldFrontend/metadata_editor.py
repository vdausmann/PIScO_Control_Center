from PySide6.QtWidgets import (
        QLineEdit, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QSpacerItem,
        QPushButton, QScrollArea, QFormLayout, QDialog
)
from PySide6.QtCore import Qt, Slot
from .styles import *



class MetaDataEditor(QDialog):
    def __init__(self, meta_data: dict = {}, parent=None):
        super().__init__(parent)
        self.meta_data = meta_data
        self.setWindowTitle("Settings Editor")
        self.setModal(True)
        self.setFixedSize(500, 700)
        self.name_inputs = []
        self.value_inputs = []
        self.name_input_width = 150
        self.value_input_width = 250

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        scroll_area = QScrollArea()

        internal_label = QLabel("Meta Data")
        internal_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #555; padding: 2px; border: none;")
        main_layout.addWidget(internal_label)

        self.form_layout = QVBoxLayout()
        self.form_layout.setContentsMargins(2, 0, 2, 0) # No extra margins for internal layout
        self.form_layout.setSpacing(0)


        for name in self.meta_data:
            row = QHBoxLayout()

            name_input = QLineEdit(name)
            name_input.setStyleSheet("font-size: 12px;")
            name_input.setFixedSize(self.name_input_width, 20)
            self.name_inputs.append(name_input)

            value_input = QLineEdit(self.meta_data[name])
            self.value_inputs.append(value_input)
            value_input.setStyleSheet("font-size: 12px;")
            value_input.setFixedSize(self.value_input_width, 20)

            row.addWidget(name_input)
            row.addWidget(value_input)
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
        self.meta_data = {}
        for i in range(len(self.name_inputs)):
            key = self.name_inputs[i].text()
            value = self.value_inputs[i].text()
            if key.strip() != "":
                self.meta_data[key] = value
        self.accept()

    def add_metadata(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        name_input = QLineEdit()
        name_input.setFixedSize(self.name_input_width, 20)
        value_input = QLineEdit()
        value_input.setFixedSize(self.value_input_width, 20)
        layout.addWidget(name_input)
        layout.addWidget(value_input)
        self.name_inputs.append(name_input)
        self.value_inputs.append(value_input)

        idx = self.form_layout.count() - 2
        self.form_layout.insertLayout(idx, layout)
        name_input.setFocus()
