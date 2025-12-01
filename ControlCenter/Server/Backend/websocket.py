from fastapi import WebSocket, WebSocketDisconnect
from .utils import endpoint

class WebSockets:

    def __init__(self) -> None:
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    @endpoint.websocket("/ws")
    async def ws_endpoint(self, ws: WebSocket):
        await self.connect(ws)
        try:
            while True:
                msg = await ws.receive_text()
                await ws.send_text(f"Server got: {msg}")
        except WebSocketDisconnect:
            print("Client disconnected cleanly")

    async def send_to_all(self, msg: str):
        for ws in self.active:
            try:
                await ws.send_text(msg)
            except:
                pass
