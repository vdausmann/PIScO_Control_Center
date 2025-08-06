import json
import requests
from Server.Backend.task_manager import Task, Module


ip = "http://localhost:8000/"

# send a taks:
m1 = Module(
        name="Test Module 1",
        settings={},
        command=["python3","/home/tim/Documents/Arbeit/PIScO_Control_Center/ControlCenter/TestModules/multicores.py"],
        num_cores=6
        )

task1 = Task(name="Test Task 1", meta_data={"Desc": "This is a test task", "ID": 1},
            modules=[m1])

id = requests.post(ip + "add-task", json=task1.model_dump()).json()
print(f"Task Id: {id}")

resp = requests.post(ip + "start-task", params={"task_id": id})
print(resp.json())

# get a task:
resp = requests.get(ip + "get-task", params={"task_id": id})
if resp.status_code == 200:
    task1 = resp.json()
    print("Task: ", task1)
else:
    print("Error: ", resp.status_code, resp.text)

