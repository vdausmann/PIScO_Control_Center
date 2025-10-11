import asyncio
from fastapi import FastAPI, HTTPException, Response, WebSocket, WebSocketDisconnect, BackgroundTasks
from contextlib import asynccontextmanager
from .task_manager import TaskManager
from .types import ChangePropertyRequest, Module, ModuleTemplate, TaskTemplate, Task
from .communication import shutdown_msg, success_msg, task_started_msg
import json
import os
import uvicorn


# Lifespan 
@asynccontextmanager
async def lifespan(app: FastAPI):
    watcher_task = asyncio.create_task(task_manager.watch_processes())
    task_manager.set_loop()

    yield  # here the app runs

    # shutdown code
    watcher_task.cancel()
    try:
        await watcher_task
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(e)

app = FastAPI(lifespan=lifespan)
connected_clients: list[WebSocket] = []
task_manager = TaskManager(connected_clients)

MODULES_SAVE_FILE = ".modules.json"

##############################################################
## HTTP endpoints:
##############################################################

@app.get("/")
async def root_endpoint():
    return True;


@app.get("/cwd")
async def get_cwd():
    return os.getcwd()

@app.post("/shutdown")
async def shutdown_endpoint():
    global uvicorn_server
    if uvicorn_server is not None:
        uvicorn_server.should_exit = True
    return shutdown_msg()


@app.post("/add-task", response_model=Task)
async def add_task_endpoint(task: TaskTemplate):
    """ Endpoint to add a task template (most likely created by the app) to the server.

    The server will convert the template to a full Task as well as all module templates
    within the task to full Modules and returns it to the client.
    For further communication between server and client, the task and each module in the
    task are assigned unique ids (task_id and module_id). The returned Task class only
    holds the modules ids and not the modules themself. To get or set the actual modules,
    further communication via the module id is needed.
    """
    return await task_manager.add_task(task)


@app.get("/get-task/{task_id}", response_model=Task)
def get_task_endpoint(task_id: str):
    try:
        return task_manager.get_task(task_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Task with Id {task_id} not found")

@app.get("/get-all-tasks", response_model=list[Task])
def get_all_task_endpoint():
    return list(task_manager.tasks.values())

@app.get("/get-module/{module_id}", response_model=Module)
def get_module_endpoint(module_id: str):
    try:
        return task_manager.get_module(module_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Module with Id {module_id} not found")

@app.get("/get-all-modules-of-task/{task_id}", response_model=list[Module])
def get_all_modules_endpoint(task_id: str):
    try:
        task = get_task_endpoint(task_id)
        modules: list[Module] = []
        for module_id in task.modules:
            modules.append(get_module_endpoint(module_id))
        return modules
    except HTTPException as e:
        raise HTTPException(e.status_code, e.detail)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Task with Id {task_id} not found")


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


@app.post("/save_state")
async def save_state_endpoint() -> dict:
    return task_manager.save_state()


@app.post("/change-task-properties/{task_id}")
async def change_task_properties_endpoint(task_id: str, req: ChangePropertyRequest):
    return await task_manager.change_task_properties(task_id, req.property_key, req.property_value)

@app.post("/change-module-properties/{module_id}")
async def change_module_properties_endpoint(module_id: str, property_key: str, property_value):
    return task_manager.change_module_properties(module_id, property_key, property_value)

@app.post("/set-module-unfinished/{module_id}")
async def set_module_unfinished_endpoint(module_id: str):
    return task_manager.set_module_unfinished(module_id)


@app.get("/get-module-templates", response_model=list[ModuleTemplate])
async def get_module_templates() -> list[ModuleTemplate]:
    with open(MODULES_SAVE_FILE, "r") as f:
        modules = json.load(f)
    return modules.values()


@app.post("/add-module-template")
async def add_module_template(module: ModuleTemplate):
    with open(MODULES_SAVE_FILE, "r") as f:
        try:
            modules = json.load(f)
        except json.JSONDecodeError:
            modules = {}
    m = module.model_dump()
    modules[module.name] = m
    with open(MODULES_SAVE_FILE, "w") as f:
        json.dump(modules, f, indent=4)
    return success_msg("Changed module templates")



##############################################################
## Websocket and process watcher task:
##############################################################

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        await websocket.send_json({"type": "Websocket connection status", "success": True})
        while True:
            msg = await websocket.receive_json()
            print("Server received message:", msg)
    except WebSocketDisconnect:
        if websocket in connected_clients:
            connected_clients.remove(websocket)
            print("Client removed")
        print("Client disconnected")


def run(host: str, port: int, remote: bool):
    global uvicorn_server
    config = uvicorn.Config(app, host=host, port=port, log_level="info",
    lifespan="on")

    uvicorn_server = uvicorn.Server(config)
    uvicorn_server.run()
