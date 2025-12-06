from typing import Optional
import h5py
import os
from threading import Timer

from numpy import isin


class HDFFileSession:
    TIMEOUT_MS = 5 * 60 # 5 minutes

    def __init__(self) -> None:
        self.file: Optional[h5py.File] = None
        self.file_path = None
        self.inactivity_timer: Optional[Timer] = None
        self.reload = False


    def open_file(self, path) -> tuple[bool, str, int]:
        if not os.path.isfile(path):
            return False, f"HDF file {path} does not exist.", 404
        try:
            if not self.file is None:
                self.file.close()

            self.file = h5py.File(path, "r")
            self.file_path = path
            self.inactive_hdf_file_path = path
            self._reset_inactivity_timer()
            return True, f"Successfully opened file {path}", 200
        except Exception as e:
            return False, f"Unknown error: {e}", 500


    def close_file(self) -> str:
        if self.file is None:
            # reset file_path upon close request which prevents reloading of an inactive
            # file
            self.file_path = None
            self.reload = False
            return "No file opened."
        try:
            self.file.close()

            if self.inactivity_timer:
                self.inactivity_timer.cancel()

            msg = f"Successfully closed file {self.file_path}."
            self.file_path = None
            self.reload = False
            return msg
        except Exception as e:
            return f"Unknown error when closing file {self.file_path}: {e}"


    def _reset_inactivity_timer(self):
        if self.inactivity_timer:
            self.inactivity_timer.cancel()
        self.inactivity_timer = Timer(self.TIMEOUT_MS, self._inactivity_timeout)
        self.inactivity_timer.start()


    def _inactivity_timeout(self):
        # store path for reloading file upon next request
        print("file is closed due to inactivity")
        current_path = self.file_path
        self.close_file()
        self.file_path = current_path
        self.reload = True


    def touch(self):
        self._reset_inactivity_timer()

    def get_path(self, path: str) -> tuple[dict, int, str]:
        if self.reload and not self.file_path is None:
            self.open_file(self.file_path)

        if self.file is None:
            return {}, 400, f"HDF file not opened"

        self._reset_inactivity_timer()

        try:
            data = self.file[path]
        except KeyError:
            return {}, 404, f"Invalid path in HDF file: {path}"

        if isinstance(data, h5py.Group):
            return {"type": "group", "members": [name for name, _ in data.items()]}, 200, ""
        elif isinstance(data, h5py.Dataset):
            return {
                "type": "dataset",
                "dtype": str(data.dtype),
                "shape": list(data.shape),
                "ndim": data.ndim,
                "chunks": data.chunks,
                "compression": data.compression,
            }, 200, ""
        else:
            raise RuntimeError(f"Data at path {path} as an type which is not currently handled")

    
    def _iterate_file(self, obj: h5py.Group | h5py.Dataset, path: str, structure: dict):
        if isinstance(obj, h5py.Group):
            structure[path] = {}
            for member, child in obj.items():
                self._iterate_file(child, path + "/" + member, structure[path])
        elif isinstance(obj, h5py.Dataset):
            structure[path] = {
                "type": "dataset",
                "dtype": str(obj.dtype),
                "shape": list(obj.shape),
                "ndim": obj.ndim,
                "chunks": obj.chunks,
                "compression": obj.compression,
            }

    def get_full_path(self, path: str) -> tuple[dict, int, str]:
        if self.reload and not self.file_path is None:
            self.open_file(self.file_path)

        if self.file is None:
            return {}, 400, f"HDF file not opened"

        self._reset_inactivity_timer()

        try:
            obj = self.file[path]
        except KeyError:
            return {}, 404, f"Invalid path in HDF file: {path}"

        if isinstance(obj, h5py.Datatype):
            return {}, 400, f"Invalid type at HDF path: {path}"

        structure = {} 
        self._iterate_file(obj, path, structure)
        return structure, 200, ""


    def get_group_structure(self, path: str) -> tuple[dict, int, str]:
        if self.reload and not self.file_path is None:
            self.open_file(self.file_path)

        if self.file is None:
            return {}, 400, f"HDF file not opened"

        self._reset_inactivity_timer()

        try:
            group = self.file[path]
        except KeyError:
            return {}, 404, f"Invalid path in HDF file: {path}."

        if not isinstance(group, h5py.Group):
            return {}, 400, f"Object at path {path} is not a group."

        structure = {"path": path, "members": {}}
        for name, obj in group.items():
            if isinstance(obj, h5py.Group):
                structure["members"][name] = "group" 
            elif isinstance(obj, h5py.Dataset):
                structure["members"][name] = "dataset" 
            else:
                structure["members"][name] = "unsupported" 

        return structure, 200, ""

    def get_data(self, path: str) -> tuple[dict, int, str]:
        if self.reload and not self.file_path is None:
            self.open_file(self.file_path)

        if self.file is None:
            return {}, 400, f"HDF file not opened"

        self._reset_inactivity_timer()

        try:
            dataset = self.file[path]
        except KeyError:
            return {}, 404, f"Invalid path in HDF file: {path}."

        if not isinstance(dataset, h5py.Dataset):
            return {}, 400, f"Object at path {path} is not a dataset."

        data = dataset[()]
        result = {"path": path, "data": data.tolist()}
        return result, 200, ""


    def get_attributes(self, path: str) -> tuple[dict, int, str]:
        if self.reload and not self.file_path is None:
            self.open_file(self.file_path)

        if self.file is None:
            return {}, 400, f"HDF file not opened"

        try:
            obj = self.file[path]
        except KeyError:
            return {}, 404, f"Invalid path in HDF file: {path}."

        return {k: v.tolist() if hasattr(v, "tolist") else v
                for k, v in obj.attrs.items()}, 200, ""


    def path_info(self, path: str) -> dict:
        if self.reload and not self.file_path is None:
            self.open_file(self.file_path)

        if self.file is None:
            raise RuntimeError("HDF file is not open (possibly timed out)")

        obj = self.file[path]
        if isinstance(obj, h5py.Group):
            return {"type": "group"}
        elif isinstance(obj, h5py.Dataset):
            return {
                "type": "dataset",
                "shape": obj.shape,
                "dtype": str(obj.dtype),
                "ndim": obj.ndim,
            }
        else:
            raise RuntimeError(f"Data at path {path} as an type which is not currently handled")
