import json
import requests
from Server.Backend.task_manager import Task, Module


ip = "http://localhost:8000/"

# send a taks:
task = Task(name="Test Task 1", meta_data={"Desc": "This is a test task", "ID": 1},
            modules=[Module(name="Test Module 1", settings={})])
id = requests.post(ip + "add-task", json=task.model_dump_json()).json()
print(f"Task Id: {id}")

resp = requests.post(ip + "start-task", params={"task_id": id})
print(resp.json())

# get a task:
resp = requests.get(ip + "get-task", params={"task_id": id})
if resp.status_code == 200:
    task = resp.json()
    print("Task: ", task)
else:
    print("Error: ", resp.status_code, resp.text)

