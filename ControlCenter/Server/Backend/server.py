import uvicorn
from fastapi import FastAPI, WebSocket
from .profile_analysis import ProfileAnalysis


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
        self.server.run()

    def _setup_routes(self):
        """Attach all endpoints to the app."""
        self.app.get("/")(self.root_endpoint)
        self.app.get("/shutdown")(self.shutdown_endpoint)
        self.app.get("/load-image-dir/{path}")(self.profile_analysis.load_image_dir_endpoint)

    async def root_endpoint(self):
        return True;

    async def shutdown_endpoint(self):
        if self.server is not None:
            self.server.should_exit = True
            return "Shutdown started"
        return "Server not running"


def create_app() -> FastAPI:
    server = PISCOServer()
    return server.app
