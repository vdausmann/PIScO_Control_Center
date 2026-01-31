from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Depends
from app.services.auth import require_user

router = APIRouter(dependencies=[Depends(require_user)])

templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def landing_page(request: Request):
    """
    Landing page / dashboard.
    """
    user = require_user(request)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "username": user["username"],
            "is_admin": user.get("is_admin", False),
        }
    )
