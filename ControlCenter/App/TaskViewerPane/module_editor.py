import json
import os
from PySide6.QtCore import Slot, QSize, Signal
from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import (QComboBox, QDialog, QHBoxLayout, QLineEdit, QPushButton, QScrollArea, QSizePolicy,
                               QVBoxLayout, QWidget, QLabel)

from Server.Backend.types import InternalModuleSettings, Module, ModuleTemplate

from ..helper import LabelEntry, clear_layout, ClickableLabel


class SettingInput(QWidget):

    deleted_signal = Signal(object)
    possible_types = ["int", "double", "string", "file", "folder"]
    
    def __init__(self, name: str = "name", type_name: str = "", parent=None) -> None:
        super().__init__(parent)
        self.type_name = QComboBox()
        self.name_input = QLineEdit()

        self.init_ui(name, type_name)

    def init_ui(self, name: str, type_name: str):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 0, 2, 0)
        layout.setSpacing(4)

        self.name_input.setText(name)
        layout.addWidget(self.name_input)

        self.type_name.addItems(self.possible_types)
        if type_name in self.possible_types:
            self.type_name.setCurrentText(type_name)
        layout.addWidget(self.type_name)

        delete_button = QPushButton()
        delete_button.setIcon(QIcon("/home/tim/Documents/Arbeit/PIScO_Control_Center/ControlCenter/App/Resources/Icons/delete_24dp_000000_FILL0_wght400_GRAD0_opsz24.png"))
        delete_button.setIconSize(QSize(18, 18))
        delete_button.setFixedSize(20, 20)
        delete_button.clicked.connect(lambda: self.deleted_signal.emit(self))

        layout.addWidget(delete_button)

    def get_name(self) -> str:
        return self.name_input.text()

    def get_type(self) -> str:
        return self.type_name.currentText()


class CreateNewModule(QDialog):

    def __init__(self, module: ModuleTemplate | None = None, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Create a new module")

        self.external_settings_inputs: list[SettingInput] = []
        self.internal_settings_inputs: dict[str, LabelEntry] = {}
        self.module = module

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        self.setFixedSize(400, 600)

        label = QLabel("Module creator")
        label.setStyleSheet("font-size: 25px; color: #456;")
        main_layout.addWidget(label)

        self.module_name = LabelEntry("Module Name", "")
        self.module_name.label.setStyleSheet("font-size: 15px; color: #456;")
        main_layout.addWidget(self.module_name)


        ###################################
        ## External Settings:
        ###################################
        label = QLabel("External Settings")
        label.setStyleSheet("font-size: 16px; color: #456;")
        main_layout.addWidget(label)

        area = QScrollArea()
        area.setWidgetResizable(True)
        area_container = QWidget()
        self.external_settings_layout = QVBoxLayout(area_container)
        self.external_settings_layout.setContentsMargins(2, 0, 2, 0)
        self.external_settings_layout.setSpacing(2)
        self.external_settings_layout.addStretch()

        area.setWidget(area_container)
        main_layout.addWidget(area, 1)

        add_setting_button = QPushButton("Add setting")
        add_setting_button.clicked.connect(self.add_external_setting_button)
        main_layout.addWidget(add_setting_button)


        ###################################
        ## Internal Settings:
        ###################################
        label = QLabel("Internal Settings")
        label.setStyleSheet("font-size: 16px; color: #456;")
        main_layout.addWidget(label)

        area = QScrollArea()
        area.setWidgetResizable(True)
        area_container = QWidget()
        self.internal_settings_layout = QVBoxLayout(area_container)
        area.setWidget(area_container)
        main_layout.addWidget(area, 1)

        # TODO: add validators
        for setting_name in InternalModuleSettings.model_fields.keys():
            setting_type = str(InternalModuleSettings.model_fields[setting_name].annotation)
            if setting_type.startswith("<class"): 
                setting_type = setting_type.split("'")[1]
            elem = LabelEntry(f"{setting_name} ({setting_type}):", "")
            self.internal_settings_inputs[setting_name] = elem
                              
            self.internal_settings_layout.addWidget(elem)
        self.internal_settings_layout.addStretch()


        main_layout.addStretch()

        button_row = QHBoxLayout()
        accept_button = QPushButton("Ok")
        accept_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_row.addWidget(accept_button)
        button_row.addWidget(cancel_button)
        main_layout.addLayout(button_row)

        # fill entries with values from given module
        if self.module is not None:
            self.module_name.entry.setText(self.module.name)
            for setting_name in self.module.settings.keys():
                self.add_external_setting(setting_name, self.module.settings[setting_name])
            internal_settings = self.module.internal_settings.model_dump()
            for key in self.internal_settings_inputs:
                if key == "command":
                    self.internal_settings_inputs[key].entry.setText(" ".join(internal_settings[key]))
                else:
                    self.internal_settings_inputs[key].entry.setText(str(internal_settings[key]))

    @Slot()
    def add_external_setting_button(self):
        self.add_external_setting()

    def add_external_setting(self, name: str="name", value: str=""):
        new_setting = SettingInput(name, value)
        self.external_settings_inputs.append(new_setting)
        new_setting.deleted_signal.connect(self.delete_external_setting)

        self.external_settings_layout.insertWidget(self.external_settings_layout.count() -
                                                   1, new_setting)

    @Slot()
    def delete_external_setting(self, setting: SettingInput):
        self.external_settings_layout.removeWidget(setting)
        self.external_settings_inputs.remove(setting)
        setting.setParent(None)
        setting.deleteLater()

    def accept(self) -> None:
        try:
            with open("App/Resources/Save/modules.json", "r") as f:
                content = f.read().strip()
            if content:
                modules = json.loads(content)
            else:
                modules = {}

            if self.module is not None:
                modules.pop(self.module.name)

            modules[self.module_name.entry.text()] = {}
            modules[self.module_name.entry.text()]["settings"] = {input.get_name(): input.get_type() for input in self.external_settings_inputs}
            internal_settings = {}
            internal_settings["command"] = self.internal_settings_inputs["command"].entry.text().split(" ")
            num_cores = self.internal_settings_inputs["num_cores"].entry.text()
            try:
                num_cores = int(num_cores)
            except ValueError:
                pass
            internal_settings["num_cores"] = num_cores
            internal_settings["priority"] = int(self.internal_settings_inputs["priority"].entry.text())
            internal_settings["order"] = int(self.internal_settings_inputs["order"].entry.text())
            modules[self.module_name.entry.text()]["internal_settings"] = internal_settings


            with open("App/Resources/Save/modules.json", "w") as f:
                json.dump(modules, f, indent=4)
        except Exception as e:
            print(e)
        return super().accept()


class EditModule(QDialog):

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Edit an existing module")

        self.selected: str | None = None
        self.labels: dict[str, ClickableLabel] = {}

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        self.setFixedSize(400, 400)

        label = QLabel("Module Editor")
        label.setStyleSheet("font-size: 25px; color: #456;")
        main_layout.addWidget(label, 1)

        area = QScrollArea()
        area_widget = QWidget()
        area_layout = QVBoxLayout(area_widget)

        with open("App/Resources/Save/modules.json", "r") as f:
            content = f.read().strip()
        if content:
            self.modules = json.loads(content)
        else:
            self.modules = {}

        for module in self.modules:
            label = ClickableLabel(module, 360)
            label.clicked_signal.connect(lambda m=module: self.module_clicked(m))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            area_layout.addWidget(label, 1, alignment=Qt.AlignmentFlag.AlignCenter)
            self.labels[module] = label

        area.setWidget(area_widget)

        main_layout.addWidget(area, 10)
        main_layout.addStretch()

        button_row = QHBoxLayout()
        accept_button = QPushButton("Ok")
        accept_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_row.addWidget(accept_button)
        button_row.addWidget(cancel_button)
        main_layout.addLayout(button_row)

    @Slot()
    def module_clicked(self, module: str):
        if self.selected is None:
            self.selected = module 
            self.labels[self.selected].clicked(True)
        elif module == self.selected:
            self.selected = None
            self.labels[module].clicked(False)
        else:
            self.labels[self.selected].clicked(False)
            self.selected = module 
            self.labels[self.selected].clicked(True)

    def get_selected(self) -> ModuleTemplate | None:
        if self.selected is None:
            return None

        m = self.modules[self.selected]
        module = ModuleTemplate(name=self.selected,
                                internal_settings=InternalModuleSettings(**m["internal_settings"]),
                                settings = m["settings"])
        return module

    def accept(self) -> None:
        return super().accept()



class AddModulesDialog(QDialog):

    def __init__(self, modules: list[Module], parent=None) -> None:
        super().__init__(parent)
        self.modules = modules
        self.inputs = {}
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        self.setFixedSize(600, 400)

        label = QLabel("Modules")
        label.setStyleSheet("font-size: 25px; color: #456;")
        main_layout.addWidget(label)


        area = QScrollArea()
        area.setWidgetResizable(True)
        area_container = QWidget()
        area_layout = QVBoxLayout(area_container)
        area.setWidget(area_container)

        area_layout.addStretch()

        main_layout.addWidget(area, 1)
        main_layout.addStretch()

        button_row = QHBoxLayout()
        accept_button = QPushButton("Ok")
        accept_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_row.addWidget(accept_button)
        button_row.addWidget(cancel_button)
        main_layout.addLayout(button_row)

    def accept(self) -> None:
        # try:
        #     self.meta_data = {key: self.inputs[key].text() for key in self.inputs}
        # except:
        #     pass
        return super().accept()


