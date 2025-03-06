from PySide6.QtWidgets import QWidget, QGridLayout, QSpacerItem, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
from PySide6.QtCore import Qt, QThread
from .LabelPathComb import LabelPathComb
from .LabelEntryComb import LabelEntryComb
from .LabelCheckboxComb import LabelCheckboxComb
from .terminal import Terminal
from .command import Command
from .inputfile_writer import write_new_inputfile
from .settings import Settings
from typing import Type

# TODO: Change grid layout to free layout and place the buttons by myself to always have the same layout for each page

class Page(QWidget):

    grid: QGridLayout

    page_elements: dict[str, Type[QWidget]] = {"LabelPathComb": LabelPathComb, "LabelEntryComb": LabelEntryComb, "LabelCheckboxComb": LabelCheckboxComb}

    def __init__(self, app, page_name: str, page_dict):
        super().__init__()

        self.app = app
        self.page_width = round(self.app.layout_settings["app_width"] * (1 - self.app.layout_settings["page_selector_width_percentage"] / 100)) - 2 * self.app.layout_settings["page_padding"]
        self.page_height = round(self.app.layout_settings["app_height"] * (1 - self.app.layout_settings["terminal_height_percentage"] / 100)) - 2 * self.app.layout_settings["page_padding"]
        self.page_name = page_name
        self.page_dict = page_dict


        self.page_layout = QVBoxLayout()
        self.label = QLabel("Settings for " + page_name, alignment=Qt.AlignCenter)
        self.page_layout.addWidget(self.label, stretch=20)

        settings_layout = QVBoxLayout()

        self.settings = Settings(page_dict)
        settings_layout.addWidget(self.settings)

        # self.settings.setLayout(self.settings_layout)
        self.page_layout.addWidget(self.settings, stretch=300)


        self.run_thread = None
        self.process = None

        button_layout = QHBoxLayout()
        button_area = QWidget()

        run_button = QPushButton("Run")
        run_button.setStyleSheet(f"background-color: {self.app.color_settings['run_button_color']}; color: {self.app.color_settings['text_color']};")
        run_button.setFixedHeight(40)
        run_button.clicked.connect(self.run_command)
        button_layout.addWidget(run_button)

        save_default_button = QPushButton("Save Default Settings")
        save_default_button.setStyleSheet(f"background-color: {self.app.color_settings['run_button_color']}; color: {self.app.color_settings['text_color']};")
        # save_default_button.setFixedSize(self.unit_width, self.unit_height)
        save_default_button.setFixedHeight(40)
        save_default_button.clicked.connect(self.save_defaults)
        button_layout.addWidget(save_default_button)

        button_area.setLayout(button_layout)
        self.page_layout.addWidget(button_area, stretch=50)

        # self.terminal_container = QWidget(self)
        self.terminal = Terminal(self.app, self)
        
        self.page_layout.addWidget(self.terminal, stretch=200)


        self.page_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.page_layout)

    def print(self, text: str):
        self.terminal.print(text)

    def run_command(self):
        if not self.run_thread is None and self.run_thread.isRunning():
            self.print("Command already running")
            return
            
        cmd = self.page_dict["runCommand"]
        if not self.page_dict["useInputFile"]:
            for key in self.settings.settings.keys():
                cmd += " --" + key + " " + str(self.settings.settings[key].get())
        else:
            path = write_new_inputfile(self.settings.settings, self.page_name)
            cmd += " " + path

        self.run_thread = QThread()
        self.command = Command(cmd, self.run_thread, self.terminal)


    def save_defaults(self):
        if not "Defaults" in self.page_dict.keys():
            self.page_dict["Defaults"] = {}
        for settings_name in self.settings.settings.keys():
            self.page_dict["Defaults"][settings_name] = self.settings.settings[settings_name].get()
        self.app.save_defaults()
