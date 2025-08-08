import asyncio
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from contextlib import asynccontextmanager
from .task_manager import TaskManager
from .types import ModuleServer, TaskClient, TaskServer
from .communication import task_started_msg

app = FastAPI()
connected_clients: list[WebSocket] = []
task_manager = TaskManager(connected_clients)

@app.post("/add-task", response_model=TaskClient)
async def add_task_endpoint(task: TaskClient):
    return task_manager.add_task(task)


@app.get("/get-task/{task_id}", response_model=TaskServer)
def get_task_endpoint(task_id: str):
    try:
        return task_manager.get_task(task_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Task with Id {task_id} not found")

@app.get("/get-all-tasks", response_model=list[TaskServer])
def get_all_task_endpoint():
    return list(task_manager.tasks.values())

@app.get("/get-module/{module_id}", response_model=ModuleServer)
def get_module_endpoint(module_id: str):
    try:
        return task_manager.get_module(module_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Task with Id {module_id} not found")


@app.post("/start-task")
async def start_task_endpoint(task_id: str, background_tasks: BackgroundTasks):
    task_manager._start_task(task_id)
    background_tasks.add_task(task_manager._run_next_modules)
    return task_started_msg(task_id)

@app.get("/trigger")
async def trigger_message_endpoint():
    for ws in connected_clients:
        await ws.send_json({"Msg": "This is a message from the server."})
    return {"status": "sent"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            await websocket.receive_json()
    except WebSocketDisconnect:
        if websocket in connected_clients:
            connected_clients.remove(websocket)
            print("Client removed")
        print("Client disconnected")

@asynccontextmanager
async def lifespan(app: FastAPI):
    watcher_task = asyncio.create_task(task_manager.watch_processes())

    yield  # here the app runs

    # shutdown code
    watcher_task.cancel()
    try:
        await watcher_task
    except asyncio.CancelledError:
        pass

app.router.lifespan_context = lifespan
