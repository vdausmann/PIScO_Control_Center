from time import sleep
import json
import requests
from Server.Backend.types import InternalModuleSettings, TaskTemplate, ModuleTemplate


ip = "http://localhost:8000/"

# send a taks:
m1 = ModuleTemplate(
        name="Test Module 1",
        settings={},
        internal_settings=InternalModuleSettings(
            command=["python3","/home/tim/Documents/Arbeit/PIScO_Control_Center/ControlCenter/TestModules/multicores.py"],
            num_cores=6,
            priority=1,
            order=1,
        )
    )

m2 = ModuleTemplate(
        name="Test Module 2",
        settings={},
        internal_settings=InternalModuleSettings(
            command=["python3","/home/tim/Documents/Arbeit/PIScO_Control_Center/ControlCenter/TestModules/multicores.py"],
            num_cores=2,
            priority=1,
            order=2
        )
    )

task1 = TaskTemplate(name="Test Task 1", meta_data={"Desc": "This is a test task", "ID": 1},
            modules=[m1])

resp = requests.post(ip + "add-task", json=task1.model_dump()).json()
id = resp["task_id"]
print(resp)
print()

resp = requests.post(ip + "start-task", params={"task_id": id})
print(resp.json(),)
print()

resp = requests.post(ip + f"change-task-properties/{id}",
                     params={"property_key": "name", "property_value": "Task 1"})
print(resp.json())
print()

# get a task:
resp = requests.get(ip + f"get-task/{id}")
if resp.status_code == 200:
    task1 = resp.json()
    module_id = resp.json()["modules"][0]
    print("Task: ", task1)
else:
    print("Error: ", resp.status_code, resp.text)
    module_id =  ""
print()

sleep(6)
resp = requests.post(ip + f"set-module-unfinished/{module_id}")
print(resp.json())
print()

resp = requests.post(ip + f"change-module-properties/{module_id}",
                     params={"property_key": "name", "property_value": "Module 1"})
print(resp.json())
print()

# get a module
resp = requests.get(ip + f"get-module/{module_id}")
if resp.status_code == 200:
    module1 = resp.json()
    print("Module: ", module1)
else:
    print("Error: ", resp.status_code, resp.text)
print()

# resp = requests.post(ip + "save_state")
# print(resp.json())
