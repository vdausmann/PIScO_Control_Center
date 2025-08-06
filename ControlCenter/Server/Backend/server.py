from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from .task_manager import Task, TaskManager

app = FastAPI()
connected_clients: list[WebSocket] = []
task_manager = TaskManager(connected_clients)

@app.post("/add-task")
async def add_task_endpoint(task: Task):
    return task_manager._add_task(task)

@app.get("/get-task", response_model=Task)
def get_task_endpoint(task_id: str):
    try:
        return task_manager._get_task(task_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

@app.post("/start-task")
async def start_task_endpoint(task_id: str):
    await task_manager._start_task(task_id)
    return {"status": "started"}

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
