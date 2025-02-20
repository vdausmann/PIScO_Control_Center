from PySide6.QtWidgets import QWidget, QGridLayout, QSpacerItem, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, QThread
from .LabelPathComb import LabelPathComb
from .LabelEntryComb import LabelEntryComb
from .LabelCheckboxComb import LabelCheckboxComb
from .terminal import Terminal
from .command import Command
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


        self.button_container = QWidget(self)
        self.button_container.setFixedSize(self.page_width, self.page_height)
        self.button_container.setStyleSheet(f"background-color: self.app.color_settings['page_background_color'];")
        self.button_container.move(self.app.layout_settings["page_padding"], self.app.layout_settings["page_padding"])

        self.terminal_container = QWidget(self)
        self.terminal_container.setFixedSize(self.page_width, self.app.layout_settings["app_height"] * self.app.layout_settings["terminal_height_percentage"] / 100 - self.app.layout_settings["page_padding"])
        self.terminal_container.setStyleSheet(f"background-color: self.app.color_settings['page_background_color'];")
        self.terminal_container.move(self.app.layout_settings["page_padding"], self.app.layout_settings["app_height"] * (1 - self.app.layout_settings["terminal_height_percentage"] / 100))

        self.terminal = Terminal(self.app, self.terminal_container)
        self.terminal.setFixedSize(self.page_width, self.app.layout_settings["app_height"] * self.app.layout_settings["terminal_height_percentage"] / 100 - self.app.layout_settings["page_padding"])


        self.grid = QGridLayout()
        self.grid.setHorizontalSpacing(5)
        self.grid.setVerticalSpacing(10)
        self.button_container.setLayout(self.grid)

        self.settings = {}

        self.unit_height = max(self.app.layout_settings["label_entry_comb_height"], self.app.layout_settings["label_path_comb_height"])
        self.unit_width = max(self.app.layout_settings["label_entry_comb_width"], self.app.layout_settings["label_path_comb_width"])
        self.numrows = self.button_container.height() // self.unit_height - 1
        self.numcols = self.button_container.width() // self.unit_width

        self.run_thread = None
        self.process = None

        self.create_page()

    def print(self, text: str):
        self.terminal.print(text)

    def run_command(self):
        if not self.run_thread is None and self.run_thread.isRunning():
            self.print("Command already running")
            return
            
        cmd = self.page_dict["runCommand"]
        if not self.page_dict["useInputFile"]:
            for key in self.settings.keys():
                cmd += " --" + key + " " + str(self.settings[key].get())

        # self.print("Running command " + cmd)
        command = Command(cmd)
        self.run_thread = QThread()
        command.moveToThread(self.run_thread)
        self.run_thread.started.connect(command.run)
        command.terminal_signal.connect(self.terminal.print)
        # self.run_thread.finished.connect(self.run_thread.deleteLater)
        print("Starting thread")
        self.run_thread.start()
        # if self.process is not None and self.process.poll() is None:
        # if not self.run_thread is None and not self.run_thread.joinable():
        #     self.print("Command already running")
        #     return
        # self.run_thread.join()



    def create_page(self):
        print(self.page_dict)
        if len(self.page_dict["Fields"].keys()) >= self.numrows * self.numcols:
            raise Warning("Too many elements in page. Make page bigger (by increasing the app_width) or make the elements smaller (by decreasing label_entry_comb_width, label_entry_comb_height)")

        idx = 0
        for settings_name in self.page_dict["Fields"].keys():
            if "Defaults" in self.page_dict.keys() and settings_name in self.page_dict["Defaults"].keys():
                default_value = self.page_dict["Defaults"][settings_name]
                l = self.page_elements[self.page_dict["Fields"][settings_name]](settings_name, self, default_value)
            else:
                l = self.page_elements[self.page_dict["Fields"][settings_name]](settings_name, self)
            self.settings[settings_name] = l
            l.setStyleSheet(f"background-color: {self.app.color_settings['button_color']}; padding: 0px;")
            l.setFixedSize(self.unit_width, self.unit_height)
            self.grid.addWidget(l, idx // self.numcols, idx % self.numcols)
            idx += 1

        # print(idx)
        new_idx = idx
        for i in range(idx, (self.numrows - 1) * self.numcols):
            new_idx += 1
            self.grid.addItem(QSpacerItem(self.unit_width, self.unit_height), (i + idx) // self.numcols, (i + idx) % self.numcols)
        print(new_idx)

        for i in range(self.numcols):
            if i == self.numcols // 2 - 1:
                self.run_button = QPushButton("Run")
                self.run_button.setStyleSheet(f"background-color: {self.app.color_settings['run_button_color']}; color: {self.app.color_settings['text_color']};")
                self.run_button.setFixedSize(self.unit_width, self.unit_height)
                self.run_button.clicked.connect(self.run_command)
                self.grid.addWidget(self.run_button, self.numrows - 1, i)
            if i == self.numcols // 2:
                self.run_button = QPushButton("Save Default Settings")
                self.run_button.setStyleSheet(f"background-color: {self.app.color_settings['run_button_color']}; color: {self.app.color_settings['text_color']};")
                self.run_button.setFixedSize(self.unit_width, self.unit_height)
                self.grid.addWidget(self.run_button, self.numrows - 1, i)
            else:
                self.grid.addItem(QSpacerItem(self.unit_width, self.unit_height), self.numrows - 1, i)
