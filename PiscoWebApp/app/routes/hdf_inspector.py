from cv2 import hdf
import numpy as np
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import plotly.graph_objects as go
from plotly.io import to_html, to_json
from fastapi import Depends

from app.services.hdf_service import HDFInspectorError, HDFPathNotFound, HDFService
from app.services.auth import require_user

router = APIRouter(dependencies=[Depends(require_user)])
templates = Jinja2Templates(directory="templates")


def plot_distribution(x, y):
    fig = go.Figure(go.Histogram(x=x, y=y, 
                                 xbins={
                                     "start": np.min(x),
                                     "end": np.max(x),
                                     "size": 0.1,
                                     }))
    fig.update_layout(
        title="Particle distribution histogram",
        margin=dict(l=20, r=20, t=30, b=20),
        height=300,
        xaxis_title="Depth in dbar",
        yaxis_title="Number of particles in bin",
    )

    # Generate HTML div (without full page)
    # plot_div = to_html(fig, full_html=False, include_plotlyjs="cdn")
    return to_json(fig)

def plot_image(img):
    # fig = go.Figure(go.Image(z=img))
    fig = go.Figure()

    fig.add_trace(go.Image(z=img))  # z = 2D array or RGB array

    fig.update_layout(
        title="Reconstructed image",
        margin=dict(l=20, r=20, t=40, b=20),
        # plot_bgcolor=bg_color,
        # paper_bgcolor=bg_color,
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False, showticklabels=False),
        height=800,
        template="plotly_dark",
    )

    # return to_html(fig, full_html=False, include_plotlyjs="cdn")
    return to_json(fig)



@router.get("/plot/{file_path:path}", response_class=JSONResponse)
def add_plot(file_path: str, hdf_path: str):
    service = HDFService(file_path)

    if not service.exists():
        return HTMLResponse("Selected file no longer exists.")

    if hdf_path == "/":
        data = service.get_distribution()
        plot = plot_distribution(data["depths"], data["num_objects"])
    else:
        img = service.reconstruct_image(hdf_path)
        plot = plot_image(img)
    return JSONResponse(plot)



@router.get("/inspect/{file_path:path}", response_class=HTMLResponse)
def inspect_hdf(request: Request, file_path: str, hdf_path: str):
    service = HDFService(file_path)

    if not service.exists():
        return HTMLResponse("Selected file no longer exists.")

    structure = service.list_groups_and_datasets(hdf_path)

    return templates.TemplateResponse(
        "inspector.html",
        {
            "request": request,
            "file_path": file_path,
            "groups": structure["groups"],
            "datasets": structure["datasets"],
            "attributes": structure["attributes"],
            "hdf_path": hdf_path,
        }
    )


def matrix_preview(data, cols=10, max_elements=200):
    data = data[:max_elements]
    vmin = float(np.min(data))
    vmax = float(np.max(data))

    def norm(v):
        if vmax == vmin:
            return 0.5
        return (v - vmin) / (vmax - vmin)

    rows = []
    for i in range(0, len(data), cols):
        row = []
        for v in data[i:i + cols]:
            row.append({
                "value": float(v),
                "norm": norm(float(v)),
            })
        rows.append(row)

    return rows, vmin, vmax

@router.get("/inspect-data/{file_path:path}", response_class=HTMLResponse)
def inspect_hdf_data(request: Request, file_path: str, hdf_path: str):
    service = HDFService(file_path)

    if not service.exists():
        return HTMLResponse("Selected file no longer exists.")

    dataset_info = service.get_dataset(hdf_path)

    full_shape = dataset_info["data"].shape
    truncated = False
    if len(dataset_info["data"]) > 1000:
        dataset_info["data"] = dataset_info["data"][:1000]
        truncated = True

    rows, vmin, vmax = matrix_preview(dataset_info["data"], cols=25,
                                      max_elements=len(dataset_info["data"]))
    return templates.TemplateResponse(
        "data_inspector.html",
        {
            "request": request,
            "file_path": file_path,
            "name": dataset_info["name"],
            "data": dataset_info["data"],
            "truncated": truncated,
            "rows": rows,
            "vmin": vmin,
            "vmax": vmax,
            "shape": full_shape,
            "dtype": dataset_info["data"].dtype,
        }
    )
