import asyncio
import os
from fastapi import HTTPException, Query, Response, status
from pydantic import BaseModel
import cv2 as cv
import numpy as np
from Utils.types import Image

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

class ProfileAnalysis:

    def __init__(self) -> None:

        self.dirpath = None
        self.image_files: list[str] = []
        self.loaded_images: dict[int, Image] = {}

        self.valid_file_extensions = [".png", ".jpg", ".tiff"]

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


    @endpoint.get("open-hdf5-file/{path:path}")
    async def open_hdf5_file(self, path: str):
        ...
