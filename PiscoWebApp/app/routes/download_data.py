from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import h5py
import numpy as np
import io
import csv

from app.services.hdf_service import HDFService

from fastapi import Depends
from app.services.auth import require_user

router = APIRouter(dependencies=[Depends(require_user)])

def dataset_to_csv_stream(ds):
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    data = ds[()]

    if data.ndim == 1:
        for v in data:
            writer.writerow([v])
    elif data.ndim == 2:
        for row in data:
            writer.writerow(row)
    else:
        raise ValueError("CSV export supports only 1D or 2D datasets")

    buffer.seek(0)
    return buffer


@router.get("/download/dataset/{file_path:path}")
def download_dataset(file_path: str, hdf_path: str):
    service = HDFService(file_path)

    dataset = service.get_dataset(hdf_path)["data"]
    stream = dataset_to_csv_stream(dataset)
    filename = hdf_path.strip("/").replace("/", "_") + ".csv"

    return StreamingResponse(
        stream,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )
