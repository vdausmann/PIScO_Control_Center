from PySide6.QtWidgets import QFrame, QPushButton, QVBoxLayout, QWidget, QSpacerItem, QScrollArea
from PySide6.QtCore import Qt
from typing import Callable

class PageSelector(QWidget):
    def __init__(self, pages: list[str], app):
        super().__init__(parent=app.main_window)


        # self.setFixedWidth(200)

        self.app = app
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        button_container = QWidget()
        button_layout = QVBoxLayout()
        # button_layout.setContentsMargins(0, 0, 0, 0)
        # button_layout.setSpacing(5)
        
        self.pages = pages
        self.buttons = []

        # button_size = (app.layout_settings["page_switch_button_width"], app.layout_settings["page_switch_button_height"])

        for index, page in enumerate(self.pages):
            button = QPushButton(page)
            # button.setFixedSize(*button_size)
            button.setStyleSheet(f"background-color: {self.app.color_settings['button_color']}; color: {self.app.color_settings['text_color']}; padding: 5px;")
            button.clicked.connect(lambda _, i=index: self.onclick(i))
            self.buttons.append(button)
            button_layout.addWidget(button)


        button_layout.addStretch()
        button_container.setLayout(button_layout)
        scroll_area.setWidget(button_container)
        
        layout.addWidget(scroll_area)

        self.setLayout(layout)
        

        self.buttons[0].setStyleSheet(f"background-color: {self.app.color_settings['button_color_clicked']}; color: {self.app.color_settings['text_color']}; padding: 5px; border-radius: 5px;")

    def onclick(self, button_id: int):
        self.app.switch_page(button_id)
        for i in range(len(self.buttons)):
            if i == button_id:
                self.buttons[i].setStyleSheet(f"background-color: {self.app.color_settings['button_color_clicked']}; color: {self.app.color_settings['text_color']}; padding: 5px;")
            else:
                self.buttons[i].setStyleSheet(f"background-color: {self.app.color_settings['button_color']}; color: {self.app.color_settings['text_color']}; padding: 5px;")
