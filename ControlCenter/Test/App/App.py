from PySide6.QtWidgets import QHBoxLayout, QStackedWidget, QWidget, QLabel, QApplication
from .page_selector import PageSelector
from .Window import Window
import sys
import json

class PIScOControlCenter:

    color_settings: dict[str, str] = {"background_color": "#404258", "page_background_color": "#404258", "page_selector_background_color": "#474E68", "button_color": "#5B88A5", "text_color": "#eef4ed", "terminal_color": "#50577A", "button_color_clicked": "#404258", "run_button_color": "red"}

    layout_settings: dict[str, int] = {"app_width": 1080, "app_height": 720, "label_entry_comb_width": 150, "label_entry_comb_height": 50, "label_path_comb_width": 150, "label_path_comb_height": 50, "page_switch_button_width": 80, "page_switch_button_height": 30, "page_selector_width_percentage": 10, "terminal_height": 200, "page_padding": 10}

    pages_settings: dict[str, dict] = {}


    def __init__(self, config_path: str):
        super().__init__()

        self.categories: dict[str, dict] = {"colors": self.color_settings, "layout": self.layout_settings, "page": self.pages_settings}

        self.config_path = config_path
        self.load_config()

        self.app = QApplication([])
        self.app.setStyleSheet(f"""
                * {{
                    color: {self.color_settings["text_color"]};
                }}
                QPushButton {{
                    background-color: {self.color_settings["button_color"]};  /* Soft Blue button */
                    color: {self.color_settings["text_color"]};  /* Button text color */
                }}
            """)

        self.main_window = QWidget()
        self.main_window.setWindowTitle("PIScO Control Center")
        self.main_window.setFixedSize(self.layout_settings["app_width"], self.layout_settings["app_height"])
        self.main_window.setStyleSheet(f"background-color: {self.color_settings['background_color']};")

        self.main_layout = QHBoxLayout(self.main_window)
        self.main_layout.setSpacing(0)

        self.create_page_selector()
        self.create_pages()
        self.load_defaults()


        # self.main_layout.setStretch(0, self.layout_settings["page_selector_ratio"])
        # self.main_layout.setStretch(self.layout_settings["page_selector_ratio"], self.layout_settings["page_ratio"])
        self.main_window.setLayout(self.main_layout)

        self.main_window.show()
        sys.exit(self.app.exec())
            
    def load_config(self):
        with open(self.config_path, "r") as f:
            config = f.read()

        # split config on categories:
        config = config.split("[")[1:]
        for category in config:
            category, values = category.split("]")
            values = values.split("\n")
            if not category in self.categories.keys():
                raise Exception(f"Unknown category {category}. Possible categories: {self.categories.keys()}")
            if category == "page":
                current_page_name = ""
                for row in values:
                    row = row.strip()
                    if not row:
                        continue
                    if "{" in row: #new page:
                        page_name = row.split("=")[0].strip()
                        current_page_name = page_name
                        self.pages_settings[page_name] = {}
                    elif "}" in row: #end of page
                       continue 
                    else: #new setting:
                        key, value = row.split("=")
                        key = key.strip()
                        value = value.strip()    
                        self.pages_settings[current_page_name][key] = value
            else:
                for value in values:
                    value = value.strip()
                    if not value or value[0] == "#":
                        continue
                    value = value.split("=")
                    value_name = value[0].strip()
                    if not value_name in self.categories[category].keys():
                        raise Exception(f"Unknown value {value_name} in category {category}. Possible values: {self.categories[category].keys()}")
                    value = type(self.categories[category][value_name])(value[1].strip())
                    self.categories[category][value_name] = value

        #
        # for key in self.categories:
        #     print(key, self.categories[key])

    def load_defaults(self):
        for page in self.pages_settings.keys():
            try:
                with open(f"App/default/{page}.json", "r") as f:
                    config = json.load(f)
                    print(config, type(config))
            except FileNotFoundError as e:
                print(e)


    def switch_page(self, index: int):
        self.stacked_widget.setCurrentIndex(index)

    def create_page_selector(self):
        self.page_selector = PageSelector(list(self.pages_settings.keys()), self)
        self.page_selector_container = QWidget()
        self.page_selector_container.setLayout(self.page_selector.layout())
        self.page_selector_container.setStyleSheet(f"background-color: {self.color_settings['page_selector_background_color']};")
        self.page_selector_container.setFixedSize(round(self.layout_settings["app_width"] * self.layout_settings["page_selector_width_percentage"] / 100), self.layout_settings["app_height"])
        self.main_layout.addWidget(self.page_selector_container)

    def create_pages(self):
        self.stacked_widget = QStackedWidget()
        self.stacked_widget_container = QWidget()
        self.stacked_widget_container.setLayout(self.stacked_widget.layout())
        self.stacked_widget_container.setStyleSheet(f"background-color: {self.color_settings['page_background_color']};")
        self.stacked_widget_container.setFixedSize(round(self.layout_settings["app_width"] * (1 - self.layout_settings["page_selector_width_percentage"] / 100)), self.layout_settings["app_height"])

        for page in self.pages_settings.keys():
            page = self.pages_settings[page]
            page_widget = Window(self)
            page_widget.create_page(page)
            self.stacked_widget.addWidget(page_widget)

        self.main_layout.addWidget(self.stacked_widget_container)
