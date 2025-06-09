from .module import Module


class Task:
    """
    A task is defined as a collection of different modules.
    The tasks runs the modules, handles priorities, communication with other tasks and
    progress tracking.
    """

    def __init__(self, name: str, modules: list[Module], active: bool = False):
        self.modules = modules
        self.name = name
        self.active = active
        self.selected_modules = [m.name for m in modules]
        self.locked = (
            False  # if a task is locked, no changes to its modules can be made
        )

    def add_module(self, module: Module):
        if not module.name in self.selected_modules:
            self.modules.append(module)
            self.selected_modules.append(module.name)
        else:  # module already in this task
            print("Module already in module list")
