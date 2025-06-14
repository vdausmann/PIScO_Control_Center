from .task import Task
from .settings import Setting, Option
import yaml


def get_setting_dict(setting: Setting) -> dict:
    res = {}
    if setting.type_name == "option":
        res["type"] = {"option": list(setting.type.options)}
    else:
        res["type"] = setting.type_name
    res["value"] = setting.value
    res["desc"] = setting.desc
    res["check"] = setting.check
    return res


def write_current_state(tasks: list[Task]):
    state = {"tasks": {}}
    for task in tasks:
        state["tasks"][task.name] = {}
        state["tasks"][task.name]["state"] = {
            "active": task.active,
            "finished": task.finished,
        }
        state["tasks"][task.name]["modules"] = {}
        for module in task.modules:
            state["tasks"][task.name]["modules"][module.name] = {
                "externalSettings": {},
                "internalSettings": {},
            }
            d = state["tasks"][task.name]["modules"][module.name]
            for setting in module.settings:
                d["externalSettings"][setting.name] = get_setting_dict(setting)
            d["internalSettings"] = {
                "command": module.command.value,
                "priority": module.priority.value,
            }

    with open("./tmp/app_state.yaml", "w") as f:
        yaml.dump(state, f, default_flow_style=False, sort_keys=False)
