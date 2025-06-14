from App.Backend import parser, Task, Module, TaskManager, TaskState
from PySide6.QtWidgets import QMainWindow, QApplication
import sys


def print_msg(text):
    print("Received", text)


def print_error(text):
    print("Error:", text)


app = QApplication()
window = QMainWindow()

modules_dict = parser.get_modules_dict_from_file("modules.yaml")
task1 = Task("Task1", [])
task1.modules = parser.load_modules_from_dict(modules_dict, task1)
task2 = Task("Task2", [])
task2.modules = parser.load_modules_from_dict(modules_dict, task2)
tasks = [task1]


task1.modules[0].process.program_error_received.connect(print_error)
task1.modules[1].process.program_error_received.connect(print_error)

task1.modules[0].process.output_received.connect(print_msg)
task1.modules[1].process.output_received.connect(print_msg)
task_manager = TaskManager()

for task in tasks:
    task_manager.add_task(task)

for task in tasks:
    task.change_state(TaskState.Active)

# task_manager.remove_task(tasks[0])

# for task in tasks:
#     task.change_state(TaskState.Inactive)

window.show()
sys.exit(app.exec())
