from .module import Module
from App.Frontend.helper import warning
from .settings import Setting, get_setting
from .task import Task, TaskState
import yaml


def load_modules_from_file(filepath, task: Task) -> list[Module]:
    with open(filepath, "r") as f:
        data = yaml.safe_load(f)
    return load_modules_from_dict(data, task)


def get_modules_dict_from_file(filepath):
    with open(filepath, "r") as f:
        data = yaml.safe_load(f)
    return data


def load_modules_from_dict(data, task: Task) -> list[Module]:
    modules: list[Module] = []
    for module in data["Modules"]:
        module_settings = data["Modules"][module]
        external_settings = []
        for setting in module_settings["externalSettings"]:
            setting_dict = module_settings["externalSettings"][setting]
            setting_type = setting_dict["type"]
            setting_value = setting_dict["value"] if "value" in setting_dict else None
            setting_desc = setting_dict["desc"] if "desc" in setting_dict else ""
            setting_check = setting_dict["check"] if "check" in setting_dict else True
            external_settings.append(
                get_setting(
                    setting, setting_type, setting_value, setting_desc, setting_check
                )
            )
        modules.append(
            Module(module, task, external_settings, module_settings["internalSettings"])
        )

    return modules


def load_app_state(filepath) -> list[Task]:
    with open(filepath, "r") as f:
        data = yaml.safe_load(f)
    tasks: list[Task] = []
    for task_name in data["tasks"]:
        state = TaskState(data["tasks"][task_name]["state"])
        # data["tasks"][task]["state"]["active"],
        # data["tasks"][task]["state"]["finished"],
        task = Task(task_name, [], state)
        task.modules = load_modules_from_dict(data["tasks"][task_name]["modules"], task)
        tasks.append(task)
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
