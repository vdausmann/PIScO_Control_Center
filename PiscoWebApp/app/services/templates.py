from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.templating import Jinja2Templates

def inject_user(request: Request):
    return {
            "user": getattr(request.state, "user", None),
            "is_admin": getattr(request.state, "is_admin", False)
            }



templates = Jinja2Templates(
    directory="templates",
    context_processors=[inject_user]
)
