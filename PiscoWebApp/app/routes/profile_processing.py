from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Depends
from app.services.auth import require_user
from app.services.templates import templates
from pprint import pprint

router = APIRouter(dependencies=[Depends(require_user)])

selected_profiles: list[str] = []

@router.get("/profile-processing", response_class=HTMLResponse)
def landing_page(request: Request):
    return templates.TemplateResponse(
        "profile_processing.html",
        {
            "request": request,
            "selected_profiles": selected_profiles,
        }
    )

@router.get("/profile-processing/add-file/{file_path:path}")
def add_file(request: Request, file_path: str):
    if not Path(file_path).exists():
        raise HTTPException(404, "File does not exist")

    if not file_path.endswith((".h5", ".hdf5")):
        raise HTTPException(400, "Invalid file type")

    if file_path and not file_path in selected_profiles:
        selected_profiles.append(file_path)

    return RedirectResponse("/profile-processing", status_code=303)

@router.get("/profile-processing/remove-file/{file_path:path}")
def remove_file(request: Request, file_path: str):
    if file_path in selected_profiles:
        selected_profiles.remove(file_path)
    return RedirectResponse("/profile-processing", status_code=303)
