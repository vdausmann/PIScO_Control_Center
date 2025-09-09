from PySide6.QtWidgets import (QDialog, QHBoxLayout, QPushButton, QScrollArea,
                               QVBoxLayout, QWidget)

from ..helper import LabelEntry

class EditMetaDataDialog(QDialog):

    template = ["Profile Name", "Profile Count", "Stored on", "Date", "Local time",
    "Station", "D ship ID"]

    def __init__(self, meta_data: dict[str, str], parent=None) -> None:
        super().__init__(parent)
        self.meta_data = meta_data
        self.inputs = {}
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        self.setFixedSize(600, 400)

        area = QScrollArea()
        area.setWidgetResizable(True)
        area_container = QWidget()
        area_layout = QVBoxLayout(area_container)
        area.setWidget(area_container)


        for key in self.template:
            value = self.meta_data[key] if key in self.meta_data else ""
            entry = LabelEntry(key, value)
            self.inputs[entry.label_text] = entry.entry
            area_layout.addWidget(entry)
        area_layout.addStretch()

        main_layout.addWidget(area, 1)
        main_layout.addStretch()

        button_row = QHBoxLayout()
        accept_button = QPushButton("Ok")
        accept_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_row.addWidget(accept_button)
        button_row.addWidget(cancel_button)
        main_layout.addLayout(button_row)

    def accept(self) -> None:
        try:
            self.meta_data = {key: self.inputs[key].text() for key in self.inputs}
        except:
            pass
        return super().accept()


