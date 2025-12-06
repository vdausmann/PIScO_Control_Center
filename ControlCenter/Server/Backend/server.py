import uvicorn
from fastapi import FastAPI, WebSocket
import sys

from .websocket import WebSockets
from .file_handler import FileHandler
from .profile_analysis import ProfileAnalysis
from .utils import endpoint


class PISCOServer(FastAPI):

    def __init__(self) -> None:
        # self.app = FastAPI(title="PISCO Server")
        super().__init__(title="PISCO Server")
        self.connected_clients: list[WebSocket] = []
        self.server = None

        self.file_handler = FileHandler()
        self.profile_analysis = ProfileAnalysis(self.file_handler)
        self.sockets = WebSockets()

        self._setup_routes()

    def run(self, host: str, port: int, remote: bool):
        config = uvicorn.Config(self, host=host, port=port, log_level="info",
        lifespan="on")
        self.server = uvicorn.Server(config)

        # with open(".server.log", "w") as f:
        #     sys.stdout = f
        #     sys.stderr = f
        try:
            self.server.run()
        except KeyboardInterrupt:
            print("Server stopped")
            self.file_handler.close_all()
        finally:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__


    def _setup_routes(self):
        """Attach all endpoints to the app."""
        self._register_endpoints(self)
        self._register_endpoints(self.file_handler)
        self._register_endpoints(self.profile_analysis)
        self._register_endpoints(self.sockets)

    def _register_endpoints(self, obj):
        """Automatically attach decorated methods to FastAPI app."""
        for attr_name in dir(obj):
            method = getattr(obj, attr_name)
            if callable(method) and hasattr(method, "_endpoint_info"):
                info = method._endpoint_info
                route_path = info["path"]
                route_method = info["method"]

                print(f"Registering: {route_method.upper()} {route_path} -> {obj.__class__.__name__}.{attr_name}")

                getattr(self, route_method)(route_path)(method)

    @endpoint.get("/")
    async def root(self):
        return True;

    @endpoint.post("/shutdown")
    async def shutdown(self):
        if self.server is not None:
            self.server.should_exit = True
            return "Shutdown started"
        return "Server not running"


    @endpoint.get("/test_ws")
    async def test_ws(self):
        await self.sockets.send_to_all("Test websocket")
        return True


def create_app() -> FastAPI:
    server = PISCOServer()

    return server
