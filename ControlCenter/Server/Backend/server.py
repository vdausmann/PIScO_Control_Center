import uvicorn
from fastapi import FastAPI, WebSocket
import sys
from .profile_analysis import ProfileAnalysis
from .utils import endpoint


class PISCOServer:

    def __init__(self) -> None:
        self.app = FastAPI(title="PISCO Server")
        self.connected_clients: list[WebSocket] = []
        self.server = None

        self.profile_analysis = ProfileAnalysis()

        self._setup_routes()

    def run(self, host: str, port: int, remote: bool):
        config = uvicorn.Config(self.app, host=host, port=port, log_level="info",
        lifespan="on")
        self.server = uvicorn.Server(config)

        with open(".server.log", "w") as f:
            sys.stdout = f
            sys.stderr = f
            try:
                self.server.run()
            finally:
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__

    def _setup_routes(self):
        """Attach all endpoints to the app."""
        self._register_endpoints(self)
        self._register_endpoints(self.profile_analysis)

    def _register_endpoints(self, obj):
        """Automatically attach decorated methods to FastAPI app."""
        for attr_name in dir(obj):
            method = getattr(obj, attr_name)
            if callable(method) and hasattr(method, "_endpoint_info"):
                info = method._endpoint_info
                route_path = info["path"]
                route_method = info["method"]

                print(f"Registering: {route_method.upper()} {route_path} -> {obj.__class__.__name__}.{attr_name}")

                getattr(self.app, route_method)(route_path)(method)

    @endpoint.get("/")
    async def root(self):
        return True;

    @endpoint.post("/shutdown")
    async def shutdown(self):
        if self.server is not None:
            self.server.should_exit = True
            return "Shutdown started"
        return "Server not running"


def create_app() -> FastAPI:
    server = PISCOServer()
    return server.app
