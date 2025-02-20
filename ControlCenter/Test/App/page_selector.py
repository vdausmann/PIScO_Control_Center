from PySide6.QtWidgets import QFrame, QPushButton, QVBoxLayout, QWidget, QSpacerItem
from typing import Callable

class PageSelector(QWidget):

    def __init__(self, pages: list[str], app):
        super().__init__()

        self.app = app
        layout = QVBoxLayout(self)
        self.pages = pages
        self.buttons = []

        button_size = (app.layout_settings["page_switch_button_width"], app.layout_settings["page_switch_button_height"])
        rows = app.layout_settings["app_height"] // (button_size[1])

        for index, page in enumerate(self.pages):
            button = QPushButton(page)
            button.setFixedSize(*button_size)
            button.setStyleSheet(f"background-color: {self.app.color_settings['button_color']}; color: {self.app.color_settings['text_color']};")
            button.clicked.connect(lambda _, i=index: self.onclick(i))
            self.buttons.append(button)
            layout.addWidget(button)
        for _ in range(len(self.pages), rows):
            layout.addItem(QSpacerItem(button_size[0], button_size[1]))

        self.buttons[0].setStyleSheet(f"background-color: {self.app.color_settings['button_color_clicked']}; color: {self.app.color_settings['text_color']};")

    def onclick(self, button_id: int):
        self.app.switch_page(button_id)
        for i in range(len(self.buttons)):
            if i == button_id:
                self.buttons[i].setStyleSheet(f"background-color: {self.app.color_settings['button_color_clicked']}; color: {self.app.color_settings['text_color']};")
            else:
                self.buttons[i].setStyleSheet(f"background-color: {self.app.color_settings['button_color']}; color: {self.app.color_settings['text_color']};")
