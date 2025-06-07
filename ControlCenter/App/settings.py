class Option:
    def __init__(self, options: list[str]):
        self.options = options

class Setting:
    def __init__(self, name: str, setting_type: str, setting_value=None):
        self.name = name
        if setting_type == "str":
            self.type = str
        elif setting_type == "int":
            self.type = int
        elif setting_type == "double":
            self.type = float
        elif setting_type == "bool":
            self.type = bool
        elif "option" in setting_type:
            options = setting_type.split("{")[-1][:-1]
            options = options.split(",")
            self.type = Option(options)

        self.value = setting_value
