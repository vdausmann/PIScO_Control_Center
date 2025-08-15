from PySide6.QtWidgets import (
        QLineEdit, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QSpacerItem, QPushButton, QScrollArea
)
from PySide6.QtCore import Qt, Signal, Slot
from typing import override

from App.NewBackend.setting import Setting
from .styles import *


# TODO: make labels editable if module is not running or finished
# class EditableLable(QWidget):

class SettingVis(QWidget):
    settings_clicked_signal = Signal(Setting)
    def __init__(self, setting: Setting = None):
        super().__init__()
        self.setting = setting

        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 10, 0)

        background = QWidget()
        background.setStyleSheet(f"background-color: {BG2}; border: 2px solid {BORDER};")
        background.setFixedHeight(20)

        background_layout = QHBoxLayout(background)
        background_layout.setContentsMargins(0, 0, 0, 0)
        background_layout.setSpacing(0)
        self.name_label = QLabel(self.setting._name)
        self.name_label.setStyleSheet("border: none; padding: 2px")
        background_layout.addWidget(self.name_label, 1)

        self.value_label = QLabel(str(self.setting._value))
        self.value_label.setStyleSheet("border: none; padding: 2px")
        background_layout.addWidget(self.value_label, 1)

        self.setting.value_changed_signal.connect(self.update_value)

        main_layout.addWidget(background, 1)
        main_layout.addStretch()

    def update_value(self):
        self.value_label.setText(str(self.setting._value))

    @override
    def mousePressEvent(self, event):
        self.settings_clicked_signal.emit(self.setting)

