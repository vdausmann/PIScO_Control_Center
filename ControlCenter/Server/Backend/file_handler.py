from fastapi import Response
from fastapi.exceptions import HTTPException
import json
from .hdf_file_session import HDFFileSession
from .utils import endpoint
from .hdf_service import ServerSideHDFFile


class FileHandler:

    def __init__(self) -> None:
        self.loaded_hdf_files: dict[str, ServerSideHDFFile] = {}

    @endpoint.post("/open-hdf-file/{file_path:path}")
    def open_hdf_file(self, file_path: str):
        file = ServerSideHDFFile()
        success, msg, code = file.open(file_path)
        if success:
            self.loaded_hdf_files[file_path] = file
            return {"msg": msg}
        raise HTTPException(status_code=code, detail=msg)


    @endpoint.post("/close-hdf-file/{file_path:path}")
    def close_hdf_file(self, file_path: str):
        if not file_path in self.loaded_hdf_files:
            raise HTTPException(status_code=404, detail=f"File {file_path} not opened")

        msg = self.loaded_hdf_files[file_path].close()
        return {"msg": msg}

    @endpoint.get("/get-hdf-keys/{path:path}")
    def get_hdf_keys(self, path: str, file_path: str):
        if not file_path in self.loaded_hdf_files:
            raise HTTPException(status_code=404, detail=f"File {file_path} not opened")

        data, msg, code = self.loaded_hdf_files[file_path].get_keys(path)

        if code != 200:
            raise HTTPException(code, msg)
        return data

    @endpoint.get("/get-hdf-dataset-info/{path:path}")
    def get_hdf_dataset_info(self, path: str, file_path: str):
        if not file_path in self.loaded_hdf_files:
            raise HTTPException(status_code=404, detail=f"File {file_path} not opened")

        data, msg, code = self.loaded_hdf_files[file_path].get_dataset_info(path)

        if code != 200:
            raise HTTPException(code, msg)
        return data


    @endpoint.get("/read-hdf-dataset/{path:path}")
    def read_hdf_dataset(self, path: str, file_path: str):
        if not file_path in self.loaded_hdf_files:
            raise HTTPException(status_code=404, detail=f"File {file_path} not opened")

        data, msg, code = self.loaded_hdf_files[file_path].read_data(path)

        if code != 200:
            raise HTTPException(code, msg)
        return Response(
                content=data.tobytes(),
                media_type="application/octet-stream",
                headers={
                    "X-Shape": json.dumps(data.shape),
                    "X-Dtype": str(data.dtype)
                }
        )

    @endpoint.get("/get-hdf-attributes/{path:path}")
    def get_hdf_attributes(self, path: str, file_path: str):
        if not file_path in self.loaded_hdf_files:
            raise HTTPException(status_code=404, detail=f"File {file_path} not opened")

        data, msg, code = self.loaded_hdf_files[file_path].get_attributes(path)
        if code != 200:
            raise HTTPException(code, msg)
        return data
