from .module import Module
from App.Frontend.helper import warning
from .settings import Setting
from .task import Task
import yaml


def load_modules_from_file(filepath) -> list[Module]:
    with open(filepath, "r") as f:
        data = yaml.safe_load(f)
    return load_modules_from_dict(data)


def load_modules_from_dict(data) -> list[Module]:
    modules: list[Module] = []
    for module in data:
        module_settings = data[module]
        external_settings = []
        for setting in module_settings["externalSettings"]:
            setting_dict = module_settings["externalSettings"][setting]
            setting_type = setting_dict["type"]
            setting_value = setting_dict["value"] if "value" in setting_dict else None
            setting_desc = setting_dict["desc"] if "desc" in setting_dict else ""
            setting_check = setting_dict["check"] if "check" in setting_dict else True
            external_settings.append(
                Setting(
                    setting, setting_type, setting_value, setting_desc, setting_check
                )
            )
        modules.append(
            Module(module, external_settings, module_settings["internalSettings"])
        )

    return modules


def load_app_state(filepath) -> list[Task]:
    with open(filepath, "r") as f:
        data = yaml.safe_load(f)
    tasks: list[Task] = []
    for task in data["tasks"]:
        tasks.append(
            Task(
                task,
                load_modules_from_dict(data["tasks"][task]["modules"]),
                data["tasks"][task]["state"]["active"],
            )
        )
    return tasks


# def load_app_state(filepath) -> tuple[dict[str, list[Module]], dict[str, list[Module]]]:
#     with open(filepath, "r") as f:
#         data = yaml.safe_load(f)
#     inactive_tasks = {}
#     for task in data["inactive_tasks"]:
#         inactive_tasks[task] = load_modules_from_dict(
#             data["inactive_tasks"][task]["modules"]
#         )
#     active_tasks = {}
#     for task in data["active_tasks"]:
#         active_tasks[task] = load_modules_from_dict(
#             data["active_tasks"][task]["modules"]
#         )
#
#     return inactive_tasks, active_tasks
