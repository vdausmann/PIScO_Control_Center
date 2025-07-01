from App.Backend import parser, Task, Module, TaskManager, TaskState
from PySide6.QtWidgets import QMainWindow, QApplication
import sys
from threading import Thread
import time

def deactivate():
    time.sleep(1)
    print("Sleep done, removing", tasks[1].name)
    tasks[1].change_state(TaskState.Inactive)
    time.sleep(2)
    print("Sleep done, reseting", tasks[0].name, tasks[0].modules[0].name)
    tasks[0].modules[0].reset()

def print_msg(text):
    print("Received", text)


def print_error(text):
    print("Error:", text)

def changed_state(state, text):
    print(state, text)


app = QApplication()
window = QMainWindow()

modules_dict = parser.get_modules_dict_from_file("app_settings.yaml")
task1 = Task("Task1", [])
task1.add_modules(parser.load_modules_from_dict(modules_dict, task1))
task2 = Task("Task2", [])
task2.add_modules(parser.load_modules_from_dict(modules_dict, task2))
tasks = [task1, task2]


for task in tasks:
    for module in task.modules:
        # module.change_state_signal.connect(changed_state)
        module.output_received_signal.connect(print_msg)

task_manager = TaskManager(2)

for task in tasks:
    task_manager.add_task(task)



for task in tasks:
    task.change_state(TaskState.Active)


# for task in tasks:
#     task.change_state(TaskState.Inactive)

t = Thread(target=deactivate)
t.start()

window.show()

sys.exit(app.exec())
