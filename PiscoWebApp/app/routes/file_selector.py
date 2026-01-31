from os import name
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from fastapi import Depends
from app.services.auth import require_user

router = APIRouter(dependencies=[Depends(require_user)])
templates = Jinja2Templates(directory="templates")

# Root directory on the server you want to browse
BROWSE_ROOT = Path.home()


@router.get("/select_file", response_class=HTMLResponse)
def select_file(request: Request, subpath: str = "", file_types: str = ""):
    """
    Simple server-side file browser.
    """
    current_path = (BROWSE_ROOT / subpath).resolve()

    if file_types:
        if "," in file_types:
            allowed_suffixes = [ft.lower().strip() for ft in file_types.split(",")]
        else:
            allowed_suffixes = [file_types.lower().strip()]
    else:
        allowed_suffixes = []

    # Security: prevent escaping outside root
    if not str(current_path).startswith(str(BROWSE_ROOT)):
        current_path = BROWSE_ROOT
        subpath = ""

    entries = []
    # Add "go up" entry if not at root
    if current_path != BROWSE_ROOT:
        parent_subpath = Path(subpath).parent
        entries.append({
            "name": "..",
            "is_dir": True,
            "is_selectable": False,
            "subpath": str(parent_subpath).replace("\\", "/"),
            "is_parent": True,
        })
    else:
        # Root has no parent
        pass

    items = list(current_path.iterdir())
    items = [i for i in items if not i.name.startswith(".")]
    items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))

    for item in items:
        entries.append({
            "name": item.name,
            "is_dir": item.is_dir(),
            "is_selectable": item.suffix.lower() in allowed_suffixes,
            "subpath": str((Path(subpath) / item.name)).replace("\\", "/"),
            "path": str((current_path / item.name))
        })

    return templates.TemplateResponse("file_selector.html", {
        "request": request,
        "entries": entries,
        "current_path": str(current_path.relative_to(BROWSE_ROOT)),
        "file_type": file_types,
        "recent": [
            {
                "path": "/home/tim/Documents/Arbeit/PIScO_Control_Center/PISCO_Modules/FullSegmenter/Results/M181-165-1_CTD-048_00°00S-017°00W_20220508-0903.h5",
                "name": "M181-165-1_CTD-048_00°00S-017°00W_20220508-0903.h5"
            },
            {
                "path":
                "/home/tim/Documents/Arbeit/PIScO_Control_Center/PISCO_Modules/FullSegmenter/Results/M202_046-01_PISCO2_20240727-0334_Images-PNG.h5",
                "name": "M202_046-01_PISCO2_20240727-0334_Images-PNG.h5"
            },
        ]
    })
