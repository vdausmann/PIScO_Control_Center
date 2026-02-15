from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Depends
import plotly.graph_objects as go


from app.services.hdf_service import HDFService
from app.services.auth import require_user
from app.services.templates import templates

from pprint import pprint

def create_hist(selected_files: list[str]):
    hdf = HDFService(selected_files[0]) 
    dist = hdf.get_distribution()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[1, 2, 3, 4],
        y=[10, 15, 13, 17],
        mode="lines+markers",
        name="Example"
    ))

    fig.update_layout(
        title="Example Plot",
    )

    # Convert to HTML snippet
    plot_html = fig.to_html(
        full_html=False,
        include_plotlyjs=True,
    )

    return plot_html



def module_hist(request: Request, selected_files: list[str]):
    print(selected_files)

    pprint(request.session)

    plot = create_hist()

    return templates.TemplateResponse(
        "module_hist.html",
        {
            "request": request,
        }
    )


