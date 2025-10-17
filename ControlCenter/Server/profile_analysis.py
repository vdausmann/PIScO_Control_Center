import os
from fastapi import HTTPException, Response, status


class ProfileAnalysis:

    def __init__(self) -> None:

        self.dirname = None
        self.image_files = []

        self.valid_file_extensions = ["png", "jpg", "tiff"]

    def _check_file_type(self, fname: str):
        for extension in self.valid_file_extensions:
            if fname.endswith(extension):
                return True
        return False

    def load_image_dir_endpoint(self, path: str):
        if os.path.isdir(path):
            self.dirname = path
            self.image_files = [f for f in os.listdir(path) if f.endswith("") if
                                self._check_file_type(f)]
            if not self.image_files:
                raise HTTPException(status_code=400, detail=f"Image directory is empty: {path}")
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            raise HTTPException(status_code=400, detail=f"Path to image directory does not exist: {path}")
