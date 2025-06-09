import os


class Option:
    def __init__(self, options: list[str]):
        self.options = options


def cast_helper(value, type_name: type):
    if value is None:
        return None
    return type_name(value)


class Setting:
    def __init__(
        self,
        name: str,
        setting_type: str | dict,
        setting_value=None,
        setting_desc: str = "",
        check: bool = True,
    ):
        self.name = name
        self.type_name = ""
        self.desc = setting_desc
        self.check = check
        if setting_type == "string":
            self.type = str
            self.type_name = setting_type
            self.value = setting_value if setting_value is not None else ""
        elif setting_type == "int":
            self.type = int
            self.type_name = setting_type
            self.value = setting_value if setting_value is not None else 0
        elif setting_type == "double":
            self.type = float
            self.type_name = setting_type
            self.value = setting_value if setting_value is not None else 0.0
        elif setting_type == "bool":
            self.type = bool
            self.type_name = setting_type
            self.value = setting_value if setting_value is not None else False
        elif type(setting_type) is dict and "option" in setting_type:
            options = setting_type["option"]
            self.type = Option(options)
            self.type_name = "option"
            self.value = setting_value if setting_value is not None else options[0]
        elif setting_type == "file":
            self.type = str
            self.type_name = setting_type
            self.value = setting_value if setting_value is not None else ""
        elif setting_type == "folder":
            self.type = str
            self.type_name = setting_type
            self.value = setting_value if setting_value is not None else "./"
