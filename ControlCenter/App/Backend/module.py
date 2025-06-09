from .settings import Setting


class Module:
    """
    A module is the collection of a run command calling an external program and the
    corresponding settings.
    """

    def __init__(self, name: str, settings: list[Setting], internal_settings: dict):
        self.name = name
        self.settings: list[Setting] = settings
        self.command = Setting("command", "string", internal_settings["command"])
        if "priority" in internal_settings:
            self.priority = Setting(
                "priority",
                "double",
                float(internal_settings["priority"]),
                "Priority of this module",
            )
        else:
            self.priority = Setting("priority", "float", 1, "Priority of this module")

    def load_settings(self, default=True): ...

    def run(self): ...
