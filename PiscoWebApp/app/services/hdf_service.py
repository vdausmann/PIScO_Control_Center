from pathlib import Path
import h5py
import numpy as np
import cv2 as cv

class HDFInspectorError(Exception):
    """Base class for all inspector errors"""


class HDFPathNotFound(HDFInspectorError):
    def __init__(self, path: str):
        super().__init__(f"HDF path not found: {path}")
        self.path = path


class HDFInvalidType(HDFInspectorError):
    def __init__(self, path: str, expected: str):
        super().__init__(f"Invalid HDF object at {path}, expected {expected}")
        self.path = path
        self.expected = expected

class HDFService:
    def __init__(self, path: str):
        self.path: Path = Path(path)

    def exists(self) -> bool:
        return self.path.exists() and self.path.is_file()

    def open(self):
        """
        Context manager style open.
        """
        return h5py.File(self.path, "r")

    def format_hdf_attrs(self, attrs, max_array_len=10):
        formatted = []

        for key, value in attrs.items():
            entry = {"key": key}

            # Bytes → string
            if isinstance(value, (bytes, bytearray)):
                entry["value"] = value.decode("utf-8", errors="replace")

            # NumPy scalar
            elif isinstance(value, np.generic):
                entry["value"] = value.item()

            # NumPy array
            elif isinstance(value, np.ndarray):
                if value.size <= max_array_len:
                    entry["value"] = value.tolist()
                else:
                    entry["value"] = (
                        f"array(shape={value.shape}, dtype={value.dtype})"
                    )

            # Fallback
            else:
                entry["value"] = value

            entry["type"] = type(value).__name__
            formatted.append(entry)

        return formatted

    def list_groups_and_datasets(self, path: str):
        """
        Returns a simple tree structure:
        {
            "groups": [...],
            "datasets": [...]
        }
        """
        result = {"groups": [], "datasets": []}

        if not path.endswith("/"):
            path += "/"

        with self.open() as f:
            if path not in f:
                raise HDFPathNotFound(path)

            group = f[path]

            if not isinstance(group, h5py.Group):
                raise HDFInvalidType(path, "group")

            for key, obj in group.items():
                if isinstance(obj, h5py.Group):
                    result["groups"].append({"name": key, "path": path + key})
                elif isinstance(obj, h5py.Dataset):
                    result["datasets"].append({"name": key, "path": path + key})

            result["attributes"] = self.format_hdf_attrs(group.attrs)

        result["groups"].sort(key=lambda x: x["name"])

        return result

    def get_dataset(self, path: str):
        dataset_info = {}
        with self.open() as f:
            if path not in f:
                raise HDFPathNotFound(path)

            dataset = f[path]

            if not isinstance(dataset, h5py.Dataset):
                raise HDFInvalidType(path, "dataset")

            dataset_info["data"] = dataset[()]
            dataset_info["name"] = dataset.name
        return dataset_info

    def get_distribution(self):
        depths = []
        num_objects = []
        with self.open() as f:
            for key, obj in f.items():
                splits = key.split("_")
                for split in splits:
                    if "dbar" in split:
                        depth = float(split.split("dbar")[0])
                        depths.append(depth)
                        break
                    elif "bar" in split:
                        depth = float(split.split("bar")[0])
                        depths.append(depth)
                        break

                num_object = obj.attrs["Number of objects"]
                num_objects.append(num_object)
        return {"depths": depths, "num_objects": num_objects}


    def reconstruct_image(self, hdf_path: str):
        img = np.ones((2560, 2560, 3), dtype=np.uint8)
        with self.open() as f:
            group = f[hdf_path]
            if not isinstance(group, h5py.Group):
                raise HDFInvalidType(hdf_path, "group")

            background_color = int(group.attrs["Mean corrected"])
            img *= background_color

            widths_group = group["width"]
            heights_group = group["height"]
            x_group = group["bx"]
            y_group = group["by"]
            pixel_data_group = group["1D_crop_data"]

            if not isinstance(widths_group, h5py.Dataset):
                raise HDFInvalidType(hdf_path, "dataset")
            if not isinstance(heights_group, h5py.Dataset):
                raise HDFInvalidType(hdf_path, "dataset")
            if not isinstance(x_group, h5py.Dataset):
                raise HDFInvalidType(hdf_path, "dataset")
            if not isinstance(y_group, h5py.Dataset):
                raise HDFInvalidType(hdf_path, "dataset")
            if not isinstance(pixel_data_group, h5py.Dataset):
                raise HDFInvalidType(hdf_path, "dataset")

            widths = widths_group[()]
            heights = heights_group[()]
            x = x_group[()]
            y = y_group[()]
            pixel_data = pixel_data_group[()]

            offset = 0
            for i in range(len(x)):
                w = widths[i]
                h = heights[i]
                pixels = pixel_data[offset:offset + w * h].reshape(h, w)
                offset += w * h

                img[y[i]:y[i]+h, x[i]:x[i]+w, 0] = pixels
                img[y[i]:y[i]+h, x[i]:x[i]+w, 1] = pixels
                img[y[i]:y[i]+h, x[i]:x[i]+w, 2] = pixels
                cv.rectangle(img, (x[i], y[i]), (x[i] + w, y[i] + h), (255, 0, 0), 4)
        img = cv.resize(img, None, fx=0.2, fy=0.2)
        # img = cv.bitwise_not(img)
        # img = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
        return img
