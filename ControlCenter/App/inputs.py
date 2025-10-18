from App.Resources.styles import BG1, BORDER
from PySide6.QtGui import QDoubleValidator, QIntValidator
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLineEdit, QWidget, QFrame


class Input(QFrame):

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setStyleSheet(f"background-color: transparent; border: none;")

        self.input = None

    def get_value(self) -> ...:
        return None


class BoolInput(Input):
    def __init__(self, value: bool = False, editable: bool = True, parent=None):
        super().__init__(parent)
        
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(value)
        self.checkbox.setEnabled(editable)
        self.checkbox.setStyleSheet(f"border: 1px solid {BORDER};")
        self.checkbox.setFixedSize(15, 15)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addStretch()
        layout.addWidget(self.checkbox)


    def get_value(self):
        return self.checkbox.isChecked()


class IntInput(Input):

    def __init__(self, value: int | None = None, editable: bool = True, validate: bool = True, min_value: int = 0, max_value: int = 10, parent=None):
        super().__init__(parent)

        self.input = QLineEdit()
        self.input.setStyleSheet(f"border: 1px solid {BORDER};")

        if value is not None:
            self.input.setText(str(value))


        if validate:
            self.validator = QIntValidator(min_value, max_value)
            self.input.textChanged.connect(self.validate)
        self.input.setReadOnly(not editable)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.input)

    def validate(self):
        state: QIntValidator.State = self.validator.validate(self.input.text(), 0)[0]
        if state != QIntValidator.State.Acceptable:
            self.input.setStyleSheet("color: red;")
        else:
            self.input.setStyleSheet("color: black;")


    def get_value(self) -> ...:
        return int(self.input.text())

class FloatInput(Input):

    def __init__(self, value: float | None = None, editable: bool = True, validate: bool = True, min_value: float = 0, max_value: float = 10,
                 decimals: int = 2, parent=None):
        super().__init__(parent)

        self.input = QLineEdit()
        self.input.setStyleSheet(f"border: 1px solid {BORDER};")
        if validate:
            self.input.setValidator(QDoubleValidator(min_value, max_value, decimals))

        if value is not None:
            self.input.setText(str(value))

        self.input.setReadOnly(not editable)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.input)

    def get_value(self) -> ...:
        return float(self.input.text())


class StringInput(Input):

    def __init__(self, value: str | None = None, editable: bool = True, parent=None):
        super().__init__(parent)

        self.input = QLineEdit()
        self.input.setStyleSheet(f"border: 1px solid {BORDER};")
        if value is not None:
            self.input.setText(value)

        self.input.setReadOnly(not editable)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.input)

    def get_value(self) -> ...:
        return float(self.input.text())

