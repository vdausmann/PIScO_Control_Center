from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Depends
from app.services.auth import require_user
from app.services.templates import templates
from pprint import pprint

router = APIRouter(dependencies=[Depends(require_user)])
# templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def landing_page(request: Request):
    """
    Landing page / dashboard.
    """
    # user = require_user(request)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
        }
    )
