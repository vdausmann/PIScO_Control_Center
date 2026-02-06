from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Depends
from app.services.auth import require_user
from app.services.templates import templates


def module_hist(request: Request, selected_files: list[str]):
    print(selected_files)
    return templates.TemplateResponse(
        "module_hist.html",
        {
            "request": request,
        }
    )
