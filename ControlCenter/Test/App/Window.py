from PySide6.QtWidgets import QWidget, QGridLayout, QSpacerItem, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt
from .LabelPathComb import LabelPathComb
from .LabelEntryComb import LabelEntryComb
from .LabelCheckboxComb import LabelCheckboxComb
from .terminal import Terminal
from typing import Type


class Window(QWidget):

    grid: QGridLayout

    page_elements: dict[str, Type[QWidget]] = {"LabelPathComb": LabelPathComb, "LabelEntryComb": LabelEntryComb, "LabelCheckboxComb": LabelCheckboxComb}

    def __init__(self, app):
        super().__init__()

        self.app = app
        self.page_width = round(self.app.layout_settings["app_width"] * (1 - self.app.layout_settings["page_selector_width_percentage"] / 100)) - self.app.layout_settings["page_padding"]

        self.window_layout = QVBoxLayout()

        self.setFixedSize(self.page_width, self.app.layout_settings["app_height"])

        self.button_container = QWidget()
        self.button_container.setFixedSize(self.page_width, self.app.layout_settings["app_height"] - self.app.layout_settings["terminal_height"])


        self.grid = QGridLayout()
        self.grid.setHorizontalSpacing(5)
        self.grid.setVerticalSpacing(10)

        self.unit_height = max(self.app.layout_settings["label_entry_comb_height"], self.app.layout_settings["label_path_comb_height"])
        self.unit_width = max(self.app.layout_settings["label_entry_comb_width"], self.app.layout_settings["label_path_comb_width"])
        self.numrows = self.button_container.height() // self.unit_height - 1
        self.numcols = self.button_container.width() // self.unit_width


        self.button_container.setLayout(self.grid)
        self.window_layout.addWidget(self.button_container)

        self.run_button = QPushButton("Run")
        self.run_button.setStyleSheet(f"background-color: {self.app.color_settings['run_button_color']}; color: {self.app.color_settings['text_color']};")
        self.run_button.setFixedSize(self.unit_width, self.unit_height)
        self.window_layout.addWidget(self.run_button, alignment=Qt.AlignCenter)

        self.terminal = Terminal(self.app)
        self.terminal.setFixedSize(self.page_width - self.app.layout_settings["page_padding"], self.app.layout_settings["terminal_height"])
        self.window_layout.addWidget(self.terminal)

        self.setLayout(self.window_layout)


    def print(self, text: str):
        self.terminal.print(text)

    def create_page(self, page: dict[str, str]):
        if len(page.keys()) >= self.numrows * self.numcols:
            raise Warning("Too many elements in page. Make page bigger (by increasing the app_width) or make the elements smaller (by decreasing label_entry_comb_width, label_entry_comb_height)")

        idx = 0
        for settings_name in page.keys():
            l = self.page_elements[page[settings_name]](settings_name, self)
            l.setStyleSheet(f"background-color: {self.app.color_settings['button_color']}; padding: 0px;")
            self.grid.addWidget(l, idx // self.numcols, idx % self.numcols)
            idx += 1

        for i in range(idx, self.numrows * self.numcols):
            self.grid.addItem(QSpacerItem(self.unit_width, self.unit_height), (i + idx) // self.numcols, (i + idx) % self.numcols)


