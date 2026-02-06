from pathlib import Path
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Depends
from app.services.auth import require_user
from app.services.templates import templates
from app.modules import module_hist
from pprint import pprint

router = APIRouter(dependencies=[Depends(require_user)])


@router.get("/profile-processing/module-hist", response_class=HTMLResponse)
def module_hist_endpoint(request: Request, selected_files: list[str] = Query(...)):
    return module_hist.module_hist(request, selected_files)
