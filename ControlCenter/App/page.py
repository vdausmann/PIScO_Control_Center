from PySide6.QtWidgets import QWidget, QGridLayout, QSpacerItem, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QFileDialog
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

        button_layout = QGridLayout()
        button_area = QWidget()

        load_config_button = QPushButton("Load Settings")
        load_config_button.setStyleSheet(f"background-color: {self.app.color_settings['run_button_color']}; color: {self.app.color_settings['text_color']};")
        # save_default_button.setFixedSize(self.unit_width, self.unit_height)
        load_config_button.setFixedHeight(40)
        load_config_button.clicked.connect(self.load_settings)
        button_layout.addWidget(load_config_button, 0, 0)

        load_default = QPushButton("Load Defaults")
        load_default.setStyleSheet(f"background-color: {self.app.color_settings['run_button_color']}; color: {self.app.color_settings['text_color']};")
        load_default.setFixedHeight(40)
        load_default.clicked.connect(self.load_defaults)
        button_layout.addWidget(load_default, 0, 1)

        save_default_button = QPushButton("Save Default Settings")
        save_default_button.setStyleSheet(f"background-color: {self.app.color_settings['run_button_color']}; color: {self.app.color_settings['text_color']};")
        save_default_button.setFixedHeight(40)
        save_default_button.clicked.connect(self.save_defaults)
        button_layout.addWidget(save_default_button, 0, 2)


        run_button = QPushButton("Run")
        run_button.setStyleSheet(f"background-color: {self.app.color_settings['run_button_color']}; color: {self.app.color_settings['text_color']};")
        run_button.setFixedHeight(40)
        run_button.clicked.connect(self.run_command)
        button_layout.addWidget(run_button, 1, 0, 1, 2)

        kill_button = QPushButton("Kill")
        kill_button.setStyleSheet(f"background-color: {self.app.color_settings['run_button_color']}; color: {self.app.color_settings['text_color']};")
        kill_button.setFixedHeight(40)
        kill_button.clicked.connect(lambda: self.command.process.kill())
        button_layout.addWidget(kill_button, 1, 2)


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
            
        args = self.page_dict["runCommand"].copy()
        if not self.page_dict["useInputFile"]:
            for key in self.settings.settings.keys():
                args.append(" --" + key)
                args.append(str(self.settings.settings[key].get()))
        else:
            path = write_new_inputfile(self.settings.settings, self.page_name)
            args.append(path)

        self.run_thread = QThread()
        self.command = Command(args, self.run_thread, self.terminal)


    def save_defaults(self):
        if not "Defaults" in self.page_dict.keys():
            self.page_dict["Defaults"] = {}
        for settings_name in self.settings.settings.keys():
            self.page_dict["Defaults"][settings_name] = self.settings.settings[settings_name].get()
        self.app.save_defaults()

    def load_defaults(self):
        if not "Defaults" in self.page_dict.keys():
            return
        for settings_name in self.settings.settings.keys():
            self.settings.settings[settings_name].set(self.page_dict["Defaults"][settings_name])

    def load_settings(self):
        file = QFileDialog.getOpenFileName(self, 'Open file', '.')[0]
        try:
            with open(file, "r") as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    # check for comment
                    if line[0] == "#" or line[0] == "//": 
                        continue
                    line = line.split("=")
                    key = line[0].strip()
                    value = line[1].strip()
                    try:
                        setting = self.settings.settings[key]
                        setting.set(setting.str_to_type(value))
                    except Exception as e:
                        print(e)
                        self.terminal.print(f'<font color="red">Error while reading key {key} from input file.</font>')

        except:
            self.terminal.print('<font color="red">Error while reading input file.</font>')
