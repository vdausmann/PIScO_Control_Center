from PySide6.QtWidgets import QHBoxLayout, QStackedWidget, QWidget, QLabel, QApplication
from .page_selector import PageSelector
from .page import Page
import sys
import json

class PIScOControlCenter:

    def __init__(self, config_path: str):
        super().__init__()

        self.config_path = config_path
        self.config = self.load_config()

        self.color_settings = self.config["colors"]
        self.layout_settings = self.config["layout"]
        self.pages_settings = self.config["pages"]

        self.app = QApplication([])

        self.main_window = QWidget()
        self.main_window.setWindowTitle("PIScO Control Center")
        self.main_window.setFixedSize(self.layout_settings["app_width"], self.layout_settings["app_height"])

        self.set_colors()
        

        self.create_page_selector()
        self.create_pages()
        
        self.main_window.show()
        sys.exit(self.app.exec())

    def set_colors(self):
        self.app.setStyleSheet(f"""
                * {{
                    color: {self.color_settings["text_color"]};
                }}
                QPushButton {{
                    background-color: {self.color_settings["button_color"]};  /* Soft Blue button */
                    color: {self.color_settings["text_color"]};  /* Button text color */
                }}
            """)
        self.main_window.setStyleSheet(f"background-color: {self.color_settings['background_color']};")
            
    def load_config(self):
        with open(self.config_path, "r") as f:
            config = json.load(f)
        return config

    def save_defaults(self):
        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=4)


    def switch_page(self, index: int):
        self.stacked_widget.setCurrentIndex(index)

    def create_page_selector(self):
        self.page_selector = PageSelector(list(self.pages_settings.keys()), self)
        self.page_selector_container = QWidget(self.main_window)
        self.page_selector_container.setLayout(self.page_selector.layout())
        self.page_selector_container.setStyleSheet(f"background-color: {self.color_settings['page_selector_background_color']};")
        self.page_selector_container.setFixedSize(round(self.layout_settings["app_width"] * self.layout_settings["page_selector_width_percentage"] / 100), self.layout_settings["app_height"])
        self.page_selector_container.move(0, 0)

    def create_pages(self):
        self.stacked_widget = QStackedWidget()
        self.stacked_widget_container = QWidget(self.main_window)
        self.stacked_widget_container.setLayout(self.stacked_widget.layout())
        self.stacked_widget_container.setStyleSheet(f"background-color: {self.color_settings['page_background_color']};")
        self.stacked_widget_container.setFixedSize(round(self.layout_settings["app_width"] * (1 - self.layout_settings["page_selector_width_percentage"] / 100)), self.layout_settings["app_height"])

        self.page_list = []
        for page in self.pages_settings.keys():
            page_dict = self.pages_settings[page]
            page_widget = Page(self, page, page_dict)
            self.page_list.append(page_widget)
            self.stacked_widget.addWidget(page_widget)

        self.stacked_widget_container.move(round(self.layout_settings["app_width"] * self.layout_settings["page_selector_width_percentage"] / 100), 0)
