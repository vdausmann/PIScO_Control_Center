from .module import Module
from .settings import Setting

def load_modules_from_file(filepath) -> list[Module]:
    modules: list[Module] = []
    with open(filepath, "r") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if not line or line[0] == "#":  # comment
                continue
            if line[0] == "[":  # new module
                if line[-1] != "]":
                    QMessageBox.warning(
                        None,
                        "Warning",
                        "Invalid line in module configuration File: "
                        + line
                        + "."
                        + "Syntax is: [Name]",
                    )
                    continue
                name = line[1:-1]
                modules.append(Module(name))
            else: #setting
                if not ":" in line:
                    QMessageBox.warning(
                        None,
                        "Warning",
                        "Invalid line in module configuration File: "
                        + line
                        + "."
                        + "Syntax is: name: type = value",
                    )
                    continue
                setting_name, setting_type = line.split(":")
                if "=" in line:
                    setting_type, value = setting_type.split("=")
                    value.strip()
                else:
                    value = None
                setting_name.strip()
                setting_type.strip()
                modules[-1].settings.append(Setting(setting_name, setting_type, value))

    return modules
