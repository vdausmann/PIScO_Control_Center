from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pathlib import Path

from fastapi import Depends
from app.services.auth import require_user
from app.services.templates import templates
from pprint import pprint
import json

router = APIRouter(dependencies=[Depends(require_user)])

# Root directory on the server you want to browse
BROWSE_ROOT = Path.home()

# load recently opened files:
recently_opened = []
recently_opened_path = "./data/recently_opened.json"
if Path(recently_opened_path).exists():
    with open(recently_opened_path, "r") as f:
        recently_opened = json.load(f)


@router.get("/select_file", response_class=HTMLResponse)
def select_file(request: Request, subpath: str = "", file_types: str = "", mode: str =
                "inpect"):
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
        "mode": mode,
        "current_path": str(current_path.relative_to(BROWSE_ROOT)),
        "file_type": file_types,
        "recent": recently_opened,
    })

@router.get("/select_file/choose/{path:path}")
def choose_file(
    request: Request,
    path: str,
    mode: str = "inspect",
):
    if mode == "inspect":
        # add to recently opened:
        found = False
        for obj in recently_opened:
            if obj["path"] == path:
                found = True
                break
        if not found:
            recently_opened.append({"path": path, "name": path.split("/")[-1]})
            with open(recently_opened_path, "w") as f:
                json.dump(recently_opened, f, indent=4)

        return RedirectResponse(f"/inspect/{path}?hdf_path=/", status_code=303)
    elif mode == "processing":
        return RedirectResponse(f"/profile-processing/add-file/{path}", status_code=303)
