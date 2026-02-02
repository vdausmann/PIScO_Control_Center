from app.services.security import init_secret_key
init_secret_key()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from starlette.middleware.sessions import SessionMiddleware
import os
from app.services.hdf_service import HDFInspectorError, HDFPathNotFound
from app.routes import landing, file_selector, hdf_inspector, download_data, auth

from app.services.templates import templates
from app.services.auth import require_user, require_admin

app = FastAPI(title="PIScO WebApp")

@app.middleware("http")
async def user_context_middleware(request: Request, call_next):
    try:
        user = require_user(request)
        if user:
            request.state.user = user.get("username")
        is_admin = require_admin(request)
        if is_admin:
            request.state.is_admin = True
        else:
            request.state.is_admin = False
    except:
        ...
    
    response = await call_next(request)
    return response


app.add_middleware(
        SessionMiddleware,
        secret_key=os.environ["SECRET_KEY"],
        session_cookie="pisco_session",
        max_age=60*120, #2hours
        same_site="lax",
        https_only=False,
)


# templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(landing.router)
app.include_router(file_selector.router)
app.include_router(hdf_inspector.router)
app.include_router(download_data.router)
app.include_router(auth.router)


@app.exception_handler(HDFPathNotFound)
def hdf_path_not_found_handler(request: Request, exc: HDFPathNotFound):
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "title": "Path not found",
            "message": f"The path '{exc.path}' does not exist in this HDF file.",
        },
        status_code=404,
    )


@app.exception_handler(HDFInspectorError)
def hdf_generic_error_handler(request: Request, exc: HDFInspectorError):
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "title": "Invalid HDF object",
            "message": str(exc),
        },
        status_code=400,
    )
