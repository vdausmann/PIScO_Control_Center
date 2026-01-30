from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request

from app.services.hdf_service import HDFInspectorError, HDFPathNotFound


from app.routes import landing, file_selector, hdf_inspector, download_data

app = FastAPI(title="PIScO WebApp")
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(landing.router)
app.include_router(file_selector.router)
app.include_router(hdf_inspector.router)
app.include_router(download_data.router)



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
