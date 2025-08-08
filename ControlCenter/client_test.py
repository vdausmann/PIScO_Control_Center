import json
import requests
from Server.Backend.types import TaskClient, ModuleClient


ip = "http://localhost:8000/"

# send a taks:
m1 = ModuleClient(
        name="Test Module 1",
        settings={},
        command=["python3","/home/tim/Documents/Arbeit/PIScO_Control_Center/ControlCenter/TestModules/multicores.py"],
        num_cores=6
        )

m2 = ModuleClient(
        name="Test Module 2",
        settings={},
        command=["python3","/home/tim/Documents/Arbeit/PIScO_Control_Center/ControlCenter/TestModules/multicores.py"],
        num_cores=2
        )

task1 = TaskClient(name="Test Task 1", meta_data={"Desc": "This is a test task", "ID": 1},
            modules=[m1])

resp = requests.post(ip + "add-task", json=task1.model_dump()).json()
id = resp["task_id"]
print(resp)
print()

resp = requests.post(ip + "start-task", params={"task_id": id})
print(resp.json(),)
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

# get a module
resp = requests.get(ip + f"get-module/{module_id}")
if resp.status_code == 200:
    module1 = resp.json()
    print("Module: ", module1)
else:
    print("Error: ", resp.status_code, resp.text)
