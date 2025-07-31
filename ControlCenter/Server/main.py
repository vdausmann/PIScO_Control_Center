from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import PlainTextResponse, JSONResponse
from pydantic import BaseModel
import os
import uuid
from fastapi import HTTPException


class Task(BaseModel):
    name: str
    # meta_data: dict
    is_running: bool = False


tasks: dict[str, Task] = {}

app = FastAPI()

os.makedirs("config", exist_ok=True)
os.makedirs("logs", exist_ok=True)


@app.post("/add-task")
async def add_task(task: Task):
    id = str(uuid.uuid4())
    tasks[id] = task
    return id

@app.get("/get-task", response_model=Task)
def get_task(task_id: str):
    if task_id in tasks:
        return tasks[task_id]
    else:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

# @app.get("/get-meta-data/{task_id}")
# async def get_meta_data(task_id: str):
#     if task_id in tasks:
#         return tasks[task_id].meta_data
#     else:
#         raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")


