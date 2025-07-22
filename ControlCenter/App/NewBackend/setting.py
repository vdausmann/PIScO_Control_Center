from PySide6.QtCore import Signal, QObject

class Setting(QObject):
    """Represents a single Setting of a module."""

    value_changed_signal = Signal()
    def __init__(self, name: str, value, setting_type: str):
        super().__init__()
        self._name = name
        self._value = value
        self._setting_type = setting_type

    def to_dict(self):
        return {"name": self._name, "value": self._value, "setting_type": self._setting_type}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data["name"], data["value"], data["setting_type"])

    def update_from_dict(self, data: dict):
        self._name = data["name"]
        self._value = data["value"]
        self._setting_type = data["setting_type"]

    def change_value(self, new_value):
        self._value = new_value
        self.value_changed_signal.emit()


if __name__ == "__main__":
    s = Setting("test", 1, "int")
    d = s.to_dict()
    print(d)
    s2 = Setting.from_dict(d)
    print(s2, s2.to_dict())
