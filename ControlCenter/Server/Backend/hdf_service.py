from typing import Optional
import h5py
import os
import numpy as np


class ServerSideHDFFile:
    def __init__(self):
        self.file_path: Optional[str] = None
        # self.file: Optional[h5py.File] = None

    def _open(self):
        if not self.file_path is None:
            self.file = h5py.File(self.file_path, "r")

    def open(self, file_path: str):
        self.file_path = file_path
        if not os.path.isfile(self.file_path):
            return False, f"HDF file {self.file_path} does not exist.", 404
        try:
            self._open()
            return True, f"Successfully opened file {self.file_path}", 200
        except Exception as e:
            return False, f"Unknown error: {e}", 500

    def close(self):
        if not self.file is None:
            self.file.close()
            return f"Successfully closed file {self.file_path}"
        return f"File {self.file_path} was not opened"

    def _get_path(self, path):
        if self.file is None:
            self._open()
        try:
            return 200, self.file[path]
        except KeyError:
            return 404, f"{path} is not in HDF file"
        except Exception as e:
            return 500, f"Unknown error: {e}"


    def get_keys(self, path: str):
        code, group = self._get_path(path)

        if code != 200 or isinstance(group, str):
            return [], group, code

        if isinstance(group, h5py.Group):
            res = {}
            for name, obj in group.items():
                if isinstance(obj, h5py.Group):
                    res[name] = "group"
                elif isinstance(obj, h5py.Dataset):
                    res[name] = "dataset"
            return res, "", 200
        else:
            return [], f"{path} is not a group", 400


    def get_dataset_info(self, path: str):
        code, obj = self._get_path(path)
        if code != 200 or isinstance(obj, str):
            return [], obj, code

        if not isinstance(obj, h5py.Dataset):
            return {}, f"{path} is not a dataset", 400

        return {
            "shape": obj.shape,
            "dtype": str(obj.dtype)
        }, "", 200


    def read_data(self, path: str):
        code, obj = self._get_path(path)
        if code != 200 or isinstance(obj, str):
            return np.array([]), obj, code

        if not isinstance(obj, h5py.Dataset):
            return np.array([]), f"{path} is not a dataset", 400

        data: np.ndarray = obj[()]
        return data, "", 200


    def get_attributes(self, path):
        code, obj = self._get_path(path)
        if code != 200 or isinstance(obj, str):
            return np.array([]), obj, code

        out = {}
        for k, v in obj.attrs.items():
            # Convert numpy scalars / arrays to JSON-friendly types
            if isinstance(v, np.ndarray):
                out[k] = v.tolist()
            elif isinstance(v, (np.integer, np.floating)):
                out[k] = v.item()
            else:
                out[k] = v
        return out, "", 200
