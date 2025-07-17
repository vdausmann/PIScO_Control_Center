
class Setting:
    """Represents a single Setting of a module."""
    def __init__(self, name: str, value, setting_type: str):
        self._name = name
        self._value = value
        self._setting_type = setting_type

    def to_dict(self):
        return {"name": self._name, "value": self._value, "setting_type": self._setting_type}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data["name"], data["value"], data["setting_type"])


if __name__ == "__main__":
    s = Setting("test", 1, "int")
    d = s.to_dict()
    print(d)
    s2 = Setting.from_dict(d)
    print(s2, s2.to_dict())
