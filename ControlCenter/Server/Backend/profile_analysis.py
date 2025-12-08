from fastapi import HTTPException
import pandas as pd
import numpy as np
import json

from .utils import endpoint
from .file_handler import FileHandler


class ProfileAnalysis:
    # This class mostly works on a hdf5 file which is loaded by the file_handler.
    # It assumes a certain structure and can only use PISCO profiles converted to HDF

    def __init__(self, file_handler: FileHandler) -> None:
        self.file_handler = file_handler
        self.profile_dataframe = None


    @endpoint.get("/get-hdf-file-abundance")
    async def get_hdf_abundance(self, file_path: str | None = None):
        if file_path is None:
            file_path = ""
        key, success = self.file_handler._get_file_session(file_path)
        if not success:
            raise HTTPException(status_code=404, detail="Path for file to close could not be found")

        file_session = self.file_handler.loaded_hdf_files[key]
        structure, code, msg = file_session.get_group_structure("/")
        if code != 200:
            raise HTTPException(status_code=code, detail=msg)
        images = list(structure["members"])
        area_data = []   # depth, area
        pressure_data = []   # depth, area
        for image in images:
            areas_dict, code, msg = file_session.get_data(f"/{image}/object_area")
            if code != 200:
                raise HTTPException(status_code=code, detail=msg)
            areas = areas_dict["data"]
            attrs, code, msg = file_session.get_attributes(f"/{image}")
            if code != 200:
                raise HTTPException(status_code=code, detail=msg)
            pressure = attrs["pressure"]
            area_data.append(areas)
            pressure_data.append(pressure)

        return {"pressures": pressure_data, "areas": area_data}

    @endpoint.get("/get-attributes-all-images")
    async def get_attributes_all_images(self, file_path: str | None = None):
        if file_path is None:
            file_path = ""
        key, success = self.file_handler._get_file_session(file_path)
        if not success:
            raise HTTPException(status_code=404, detail="Path for file to close could not be found")

        file_session = self.file_handler.loaded_hdf_files[key]
        structure, code, msg = file_session.get_group_structure("/")
        if code != 200:
            raise HTTPException(status_code=code, detail=msg)
        images = list(structure["members"])
        data = {}
        for image in images:
            attrs, code, msg = file_session.get_attributes(f"/{image}")
            if code != 200:
                raise HTTPException(status_code=code, detail=msg)
            for key, value in attrs.items():
                if not key in data:
                    data[key] = []
                data[key].append(value)

        return data
