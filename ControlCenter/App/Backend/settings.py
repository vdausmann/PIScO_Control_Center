import os
from PySide6.QtCore import QObject, Signal


class Option:
    def __init__(self, options: list[str]):
        self.options = options


def cast_helper(value, type_name: type):
    if value is None:
        return None
    return type_name(value)


class Setting(QObject):

    def __init__(self, name: str, setting_desc: str):
        super().__init__()
        self.name = name
        self.desc = setting_desc
        

    def set_value(self, value):
        self.value = value


class StringSetting(Setting):
    value_changed_signal = Signal(str)

    def __init__(self, name: str, setting_value: str = "", setting_desc: str = ""):
        super().__init__(name, setting_desc)
        self.value = setting_value

    def set_value(self, value: str):
        self.value = value
        self.value_changed_signal.emit(self.value)


class IntSetting(Setting):
    value_changed_signal = Signal(int)

    def __init__(self, name: str, setting_value: int = 0, setting_desc: str = ""):
        super().__init__(name, setting_desc)
        self.value = setting_value

    def set_value(self, value: int):
        self.value = value
        self.value_changed_signal.emit(self.value)


class DoubleSetting(Setting):
    value_changed_signal = Signal(float)

    def __init__(self, name: str, setting_value: float = 0, setting_desc: str = ""):
        super().__init__(name, setting_desc)
        self.value = setting_value

    def set_value(self, value: float):
        self.value = value
        self.value_changed_signal.emit(self.value)

class BoolSetting(Setting):
    value_changed_signal = Signal(bool)

    def __init__(self, name: str, setting_value: bool = False, setting_desc: str = ""):
        super().__init__(name, setting_desc)
        self.value = setting_value

    def set_value(self, value: bool):
        self.value = value
        self.value_changed_signal.emit(self.value)


class OptionSetting(Setting):
    value_changed_signal = Signal(str)

    def __init__(
        self,
        name: str,
        setting_options: Option,
        setting_value: str = "",
        setting_desc: str = "",
    ):
        super().__init__(name, setting_desc)
        self.options = setting_options
        if setting_value in self.options.options:
            self.value = setting_value
        else:
            self.value = self.options.options[0]

    def set_value(self, value: str):
        if value in self.options.options:
            self.value = value
            self.value_changed_signal.emit(self.value)


class FileSetting(Setting):
    value_changed_signal = Signal(str)

    def __init__(
        self,
        name: str,
        setting_value: str = "",
        setting_desc: str = "",
    ):
        super().__init__(name, setting_desc)
        self.value = setting_value

    def set_value(self, value: str):
        self.value = value
        self.value_changed_signal.emit(self.value)


class FolderSetting(Setting):
    value_changed_signal = Signal(str)

    def __init__(
        self,
        name: str,
        setting_value: str = "./",
        setting_desc: str = "",
    ):
        super().__init__(name, setting_desc)
        self.value = setting_value

    def set_value(self, value: str):
        self.value = value
        self.value_changed_signal.emit(self.value)

def get_setting(
    name: str,
    setting_type: str | dict,
    setting_value=None,
    setting_desc: str = "",
    check: bool = True,
) -> Setting:
    if setting_type == "string":
        value = setting_value if setting_value is not None else ""
        return StringSetting(name, value, setting_desc)
    elif setting_type == "int":
        value = setting_value if setting_value is not None else 0
        return IntSetting(name, value, setting_desc)
    elif setting_type == "double":
        value = setting_value if setting_value is not None else 0.0
        return DoubleSetting(name, value, setting_desc)
    elif setting_type == "bool":
        value = setting_value if setting_value is not None else False
        return BoolSetting(name, value, setting_desc)
    elif type(setting_type) is dict and "option" in setting_type:
        options = Option(setting_type["option"])
        value = (
            setting_value if setting_value is not None else setting_type["option"][0]
        )
        return OptionSetting(name, options, value, setting_desc)
    elif setting_type == "file":
        value = setting_value if setting_value is not None else ""
        return FileSetting(name, value, setting_desc)
    elif setting_type == "folder":
        value = setting_value if setting_value is not None else "./"
        return FolderSetting(name, value, setting_desc)
    else:
        raise ValueError
