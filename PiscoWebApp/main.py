from fastapi import FastAPI, Request, Form, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import h5py, os, numpy as np, plotly.graph_objects as go, plotly.io as pio
import subprocess, uuid

DATA_DIR = "data"

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

tasks = {}  # store running tasks

# ------------------- Landing Page -------------------
@app.get("/", response_class=HTMLResponse)
def landing_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ------------------- HDF5 Browser -------------------
def list_hdf_files():
    if not os.path.exists(DATA_DIR):
        return []
    return [f for f in os.listdir(DATA_DIR) if f.endswith((".h5", ".hdf5"))]

def build_tree(h5file):
    def node_to_dict(obj):
        if isinstance(obj, h5py.Dataset):
            return {"type": "dataset"}
        elif isinstance(obj, h5py.Group):
            return {"type": "group", "children": {k: node_to_dict(v) for k, v in obj.items()}}
    return {k: node_to_dict(v) for k, v in h5file.items()}

@app.get("/files", response_class=HTMLResponse)
def files_page(request: Request):
    files = list_hdf_files()
    # Build a tree where top-level entries are files
    tree = {}
    for f in files:
        tree[f] = {"type": "group", "children": {}}  # empty children for now
    return templates.TemplateResponse("view.html", {"request": request, "filename": "Files", "tree": tree})

@app.get("/view/{filename}", response_class=HTMLResponse)
def view_file(request: Request, filename: str):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(404)
    with h5py.File(path, "r") as f:
        tree = build_tree(f)
    return templates.TemplateResponse("view.html", {"request": request, "filename": filename, "tree": tree})

# ------------------- Dataset Preview -------------------
@app.get("/dataset/{filename}/{dataset_path:path}", response_class=HTMLResponse)
def dataset_view(request: Request, filename: str, dataset_path: str):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(404)
    with h5py.File(path, "r") as f:
        if dataset_path not in f:
            raise HTTPException(404)
        dset = f[dataset_path]
        shape = dset.shape
        dtype = str(dset.dtype)
        attrs = {k: str(v) for k, v in dset.attrs.items()}

        plot_div = None
        if np.prod(shape) <= 200_000 and np.issubdtype(dset.dtype, np.number):
            data = dset[()]
            fig = None
            if data.ndim == 1:
                fig = go.Figure(go.Scatter(y=data))
            elif data.ndim == 2:
                fig = go.Figure(go.Heatmap(z=data))
            if fig is not None:
                fig.update_layout(margin=dict(l=20,r=20,t=30,b=20), height=400)
                plot_div = pio.to_html(fig, full_html=False)
    return templates.TemplateResponse("dataset.html", {"request": request, "filename": filename, "path": dataset_path, "shape": shape, "dtype": dtype, "attrs": attrs, "plot_div": plot_div})

# ------------------- Group Histogram -------------------
@app.get("/dataset_histogram/{filename}/{dataset_path:path}", response_class=HTMLResponse)
def dataset_histogram(request: Request, filename: str, dataset_path: str):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(404)
    all_data = []
    with h5py.File(path, "r") as f:
        def collect_dataset(group):
            for name, item in group.items():
                if isinstance(item, h5py.Group):
                    collect_dataset(item)
                elif isinstance(item, h5py.Dataset) and name == dataset_path.split("/")[-1]:
                    if np.issubdtype(item.dtype, np.number):
                        all_data.append(item[()].flatten())
        collect_dataset(f)

    if not all_data:
        return templates.TemplateResponse("dataset.html", {"request": request, "filename": filename, "path": dataset_path, "shape": "N/A", "dtype": "N/A", "attrs": {}, "plot_div": "<i>No numeric datasets found in groups.</i>"})

    combined_data = np.concatenate(all_data)
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=combined_data, nbinsx=50, name=dataset_path.split("/")[-1]))
    fig.update_layout(title=f"Histogram of '{dataset_path.split('/')[-1]}' across all groups", xaxis_title=dataset_path.split("/")[-1], yaxis_title="Count", height=400)
    plot_div = pio.to_html(fig, full_html=False)
    return templates.TemplateResponse("dataset.html", {"request": request, "filename": filename, "path": dataset_path, "shape": combined_data.shape, "dtype": str(combined_data.dtype), "attrs": {}, "plot_div": plot_div})

# ------------------- Run Analysis Tasks -------------------
@app.get("/run_task", response_class=HTMLResponse)
def run_task_form(request: Request):
    return templates.TemplateResponse("run_task.html", {"request": request})

def execute_program(task_id: str, param1: str, param2: int):
    cmd = ["python", "my_script.py", param1, str(param2)]
    proc = subprocess.Popen(cmd)
    tasks[task_id]["process"] = proc
    proc.wait()
    tasks[task_id]["status"] = "finished"

@app.post("/run_task", response_class=HTMLResponse)
def run_task(request: Request, background_tasks: BackgroundTasks, param1: str = Form(...), param2: int = Form(...)):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "running", "process": None}
    background_tasks.add_task(execute_program, task_id, param1, param2)
    return f"""
    <html>
        <body>
            <p>Task {task_id} started!</p>
            <p>Param1={param1}, Param2={param2}</p>
            <a href="/task_status/{task_id}">Check status</a><br>
            <a href="/">⬅ Back to Dashboard</a>
        </body>
    </html>
    """

@app.get("/task_status/{task_id}", response_class=HTMLResponse)
def task_status(task_id: str):
    if task_id not in tasks:
        return f"Task {task_id} not found"
    status = tasks[task_id]["status"]
    return f"Task {task_id} status: {status} <br><a href='/'>⬅ Back to Dashboard</a>"
