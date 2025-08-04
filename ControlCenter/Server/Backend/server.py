from fastapi import FastAPI, HTTPException
from .task_manager import Task, TaskManager

app = FastAPI()
task_manager = TaskManager()

@app.post("/add-task")
async def add_task(task: Task):
    return task_manager.add_task(task)

@app.get("/get-task", response_model=Task)
def get_task(task_id: str):
    try:
        return task_manager.get_task(task_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

@app.post("/start-task")
async def start_task(task_id: str):
    return task_manager.start_task(task_id)
