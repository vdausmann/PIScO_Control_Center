from typing import Optional
import os
import requests
import json
import numpy as np
from .server_client import ServerClient
from urllib.parse import quote


class RemoteHDFFile:

    def __init__(self, server_client: ServerClient, file_path: str) -> None:
        self.file_path: str = file_path
        self.server = server_client


    def open(self) -> tuple[int, dict]:
        req = requests.post(self.server.get_url() +
                            f"/open-hdf-file/{quote(self.file_path)}")
        return req.status_code, req.json()


    def close(self):
        """This method is a destructor of this class! Only call this method if the object
        is not used after as this will lead to invalid method calls later."""
        requests.post(self.server.get_url() +
                            f"/close-hdf-file/{quote(self.file_path)}")

    def get_keys(self, path: str):
        req = requests.get(self.server.get_url() +
                           f"/get-hdf-keys/{quote(path)}", {"file_path": self.file_path})
        return req.status_code, req.json()

    def get_dataset_info(self, path: str):
        req = requests.get(self.server.get_url() +
                           f"/get-hdf-dataset-info/{quote(path)}", {"file_path": self.file_path})
        return req.status_code, req.json()

    def get_attributes(self, path: str):
        req = requests.get(self.server.get_url() +
                           f"/get-hdf-attributes/{quote(path)}", {"file_path": self.file_path})
        return req.status_code, req.json()

    def __getitem__(self, path: str):
        req = requests.get(self.server.get_url() +
                           f"/read-hdf-dataset/{quote(path)}", {"file_path": self.file_path})
        if req.status_code != 200:
            raise RuntimeError(f"Network error {req.status_code}: " + req.json())

        shape = tuple(json.loads(req.headers["X-Shape"]))
        dtype = np.dtype(req.headers["X-Dtype"])
        data = np.frombuffer(req.content, dtype=dtype)
        return data.reshape(shape)
