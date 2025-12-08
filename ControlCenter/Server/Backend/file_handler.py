import asyncio
import os
from typing import Optional
from fastapi import HTTPException, Query, Response
from pydantic import BaseModel
import cv2 as cv
from .hdf_file_session import HDFFileSession
from Utils.types import Image
import h5py
import uuid

from PySide6.QtCore import QTimer

from .utils import endpoint


class ImageLoadRequest(BaseModel):
    start: int
    stop: int
    color_code: int = cv.IMREAD_COLOR
    unload_previous_images: bool = True

class ImageDownloadRequest(BaseModel):
    index: int
    shape: tuple[int, int] | None = None
    color_code: int = cv.IMREAD_COLOR

class FileHandler:

    TIMEOUT_MS = 5 * 1000  # 5 Minutes

    def __init__(self) -> None:

        self.dirpath = None
        self.image_files: list[str] = []
        self.loaded_images: dict[int, Image] = {}

        self.loaded_hdf_files: dict[str, HDFFileSession] = {}

        self.valid_file_extensions = [".png", ".jpg", ".tiff", ".tif"]


    def close_all(self):
        while self.loaded_hdf_files:
            path, file_session = self.loaded_hdf_files.popitem()
            file_session.close_file()
            print("Closed file", path)


    def _check_file_type(self, fname: str):
        for extension in self.valid_file_extensions:
            if fname.endswith(extension):
                return True
        return False

    async def _load_image(self, index: int, color_code: int) -> Image:
        if not self.image_files or self.dirpath is None:
            raise HTTPException(status_code=400, detail=f"No image directory loaded")
        path = os.path.join(self.dirpath, self.image_files[index])
        img = await asyncio.to_thread(cv.imread, path, color_code)
        return Image(self.image_files[index], img, color_code)

    @endpoint.post("/load-image-dir/{path:path}")
    async def load_image_dir(self, path: str):
        if os.path.isdir(path):
            self.dirpath = path
            self.image_files = [f for f in os.listdir(path) if f.endswith("") if
                                self._check_file_type(f)]
            self.image_files.sort()
            if not self.image_files:
                raise HTTPException(status_code=404, detail=f"Image directory is empty: {path}")
            return {"msg": f"Successfully loaded folder {path}", "count":
                    len(self.image_files), "files": self.image_files}
        else:
            raise HTTPException(status_code=404, detail=f"Path to image directory does not exist: {path}")

    @endpoint.post("/load-images")
    async def load_images(self, request: ImageLoadRequest):
        """Loads a range of images into the servers RAM for further processing."""
        if not self.image_files or self.dirpath is None:
            raise HTTPException(status_code=400, detail=f"No image directory loaded")
        try:
            loaded_images = list(
                    await asyncio.gather(
                        *[self._load_image(index, request.color_code) for index in range(request.start, request.stop)]
                        )
                    )
            if request.unload_previous_images:
                self.loaded_images.clear()
            c = 0
            for i in range(request.start, request.stop):
                self.loaded_images[i] = loaded_images[c]
                c += 1
            return {"msg": f"Successfully loaded {len(self.loaded_images)} images into memory."}
        except IndexError:
            raise HTTPException(status_code=400, detail=f"Invalid index range: {request.start}:{request.stop}")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Unknown error: {e}")


    @endpoint.get("/download-image")
    async def download_image(self,
            index: int = Query(..., description="Index of the image"), 
            color_code: int = Query(cv.IMREAD_COLOR, description="OpenCV color code"),
            width: int | None = Query(None, description="Optional resize shape"),
            height: int | None = Query(None, description="Optional resize shape"),
         ):
        if not self.image_files or self.dirpath is None:
            raise HTTPException(status_code=400, detail=f"No image directory loaded")

        try:
            shape = None
            if width is not None and height is not None:
                shape = (width, height)
            if not index in self.loaded_images:
                image = await self._load_image(index, color_code)
            else:
                image = self.loaded_images[index]

            if shape is not None and image.data.shape != shape:
                image.data = cv.resize(image.data, shape)
            if image.color_code != color_code:
                image.data = cv.cvtColor(image.data, color_code)
            
            success, encoded = cv.imencode(".png", image.data)
            if not success:
                raise HTTPException(status_code=500, detail=f"Failed encoding the image to png")
            return Response(content=encoded.tobytes(), media_type="image/png")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error while preparing image for download: {e}")


    #######################################
    ### HDF File handling
    #######################################

    def _get_file_session(self, file_path: str = "") -> tuple[str, bool]:
        if file_path in self.loaded_hdf_files: 
            return file_path, True
        elif len(self.loaded_hdf_files) == 1:
            return list(self.loaded_hdf_files)[0], True
        else:
            return "", False

    @endpoint.post("/open-hdf5-file/{path:path}")
    async def open_hdf5_file(self, path: str):
        if path in self.loaded_hdf_files:
            # nothing to do here
            return

        file_session = HDFFileSession()
        success, msg, code = file_session.open_file(path)

        if success:
            self.loaded_hdf_files[path] = file_session
            return {"msg": msg}
        raise HTTPException(status_code=code, detail=msg)


    @endpoint.post("/close-hdf5-file")
    async def close_hdf5_file(self, path: str | None = None):
        if path is None:
            path = ""
        key, success = self._get_file_session(path)
        if not success:
            raise HTTPException(status_code=404, detail="Path for file to close could not be found")

        file_session = self.loaded_hdf_files.pop(key)
        msg = file_session.close_file()
        return {"msg": msg}
                

    @endpoint.get("/get-path/{path:path}")
    async def get_path(self, path: str, file_path: str | None = None):
        if file_path is None:
            file_path = ""
        key, success = self._get_file_session(file_path)
        if not success:
            raise HTTPException(status_code=404, detail="Path for file to close could not be found")

        file_session = self.loaded_hdf_files[key]
        structure, code, msg = file_session.get_path(path)
        if code != 200:
            raise HTTPException(status_code=code, detail=msg)
        return structure


    @endpoint.get("/get-full-path/{path:path}")
    async def get_full_path(self, path: str, file_path: str | None = None):
        if file_path is None:
            file_path = ""
        key, success = self._get_file_session(file_path)
        if not success:
            raise HTTPException(status_code=404, detail="Path for file to close could not be found")

        file_session = self.loaded_hdf_files[key]
        structure, code, msg = file_session.get_full_path(path)
        if code != 200:
            raise HTTPException(status_code=code, detail=msg)
        return structure


    @endpoint.get("/get-group-structure/{path:path}")
    async def get_group_structure(self, path: str, file_path: str | None = None):
        if file_path is None:
            file_path = ""
        key, success = self._get_file_session(file_path)
        if not success:
            raise HTTPException(status_code=404, detail="Path for file to close could not be found")

        file_session = self.loaded_hdf_files[key]
        structure, code, msg = file_session.get_group_structure(path)
        if code != 200:
            raise HTTPException(status_code=code, detail=msg)
        return structure


    @endpoint.get("/get-data/{path:path}")
    async def get_data(self, path: str, file_path: str | None = None):
        if file_path is None:
            file_path = ""
        key, success = self._get_file_session(file_path)
        if not success:
            raise HTTPException(status_code=404, detail="Path for file to close could not be found")

        file_session = self.loaded_hdf_files[key]
        data, code, msg = file_session.get_data(path)
        if code != 200:
            raise HTTPException(status_code=code, detail=msg)
        return data


    @endpoint.get("/get-attributes/{path:path}")
    async def get_attributes(self, path: str, file_path: str | None = None):
        if file_path is None:
            file_path = ""
        key, success = self._get_file_session(file_path)
        if not success:
            raise HTTPException(status_code=404, detail="Path for file to close could not be found")

        file_session = self.loaded_hdf_files[key]
        attributes, code, msg = file_session.get_attributes(path)
        if code != 200:
            raise HTTPException(status_code=code, detail=msg)
        return attributes


# def _serialize_h5_group(self, group, recursiv: bool = False):
#     result = {}
#     for name, obj in group.items():
#         if isinstance(obj, h5py.Group):
#             if recursiv:
#                 result[name] = {}
#                 result[name]["type"] = "group"
#                 result[name]["attributes"] = {key: value for key, value in obj.attrs.items()}
#                 result[name]["structure"] = self._serialize_h5_group(obj, True)
#             else:
#                 result[name] = {}
#         elif isinstance(obj, h5py.Dataset):
#             result[name] = {
#                 "type": "data",
    #                 "shape": list(obj.shape),
    #                 "dtype": str(obj.dtype),
    #             }
    #     return result
    #
    # def _get_data_from_hdf_file(self, data_path: str):
    #     if self.loaded_hdf_file is None:
    #         raise HTTPException(status_code=400, detail=f"No HDF file opened")
    #     data = self.loaded_hdf_file[data_path]
    #     data_type = None
    #     if isinstance(data, h5py.Group):
    #         data = {"type": "group", "structure": self._serialize_h5_group(data),
    #                 "attributes": {key: value for key, value in data.attrs.items()},
    #                 "path": data_path}
    #         data_type = "group"
    #     elif isinstance(data, h5py.Dataset): 
    #         data_type = data.attrs["type"]
    #         data = data[()]
    #
    #         if data_type == "image":
    #             success, encoded = cv.imencode(".png", data)
    #             if not success:
    #                 raise HTTPException(status_code=500, detail=f"Failed encoding the image to png")
    #             data = encoded.tobytes()
    #     return data, data_type
    #
    #
    # @endpoint.get("/get-hdf5-file-data/{data_path:path}")
    # async def get_data_from_hdf_file(self, data_path: str):
    #     if self.loaded_hdf_file is None:
    #         raise HTTPException(status_code=400, detail=f"No HDF file opened")
    #
    #     try:
    #         data, data_type = self._get_data_from_hdf_file(data_path)
    #         if data_type == "group":
    #             return data
    #         elif data_type == "image":
    #             return Response(content=data, media_type="image/png",
    #                             headers={"type": "image"})
    #         elif data_type == "dict":
    #             return Response(content=data, media_type="application/json")
    #         else:
    #             raise HTTPException(status_code=500, detail=f"Could not process HDF data.")
    #     except KeyError:
    #         raise HTTPException(status_code=404, detail=f"Invalid path to HDF file data: {data_path}")
    #     except Exception as e:
    #         raise HTTPException(status_code=500, detail=f"Error while trying to access data from HDF file: {e}")
    #
    # @endpoint.get("/get-hdf5-file-structure/{starting_path:path}")
    # async def get_hdf_structure(self, starting_path: str):
    #     if self.loaded_hdf_file is None:
    #         raise HTTPException(status_code=400, detail=f"No HDF file opened")
    #     data = self.loaded_hdf_file[starting_path]
    #     structure = {}
    #     structure["structure"] = self._serialize_h5_group(data, True)
    #     structure["root"] = starting_path
    #     return structure
