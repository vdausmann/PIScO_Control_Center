import numpy as np
import cv2 as cv
import h5py 


def get_group_dataset(group: h5py.Group, name: str):
    ds = group[name]
    if not isinstance(ds, h5py.Dataset):
        raise KeyError(f"Path {name} of group {group} is not a dataset.")
    return ds[()]

def get_crop(crop_data: np.ndarray, widths: np.ndarray, heights: np.ndarray, idx: int):
    offset = (widths[:idx] * heights[:idx]).sum()
    data1D = crop_data[offset:offset + widths[idx] * heights[idx]]
    data2D = data1D.reshape((heights[idx], widths[idx]))
    return data2D


path = "./Results/M181-165-1_CTD-048_00°00S-017°00W_20220508-0903.h5"

with h5py.File(path, "r") as f:
    # crop_data = np.array([])
    # widths = np.array([])
    # heights = np.array([])
    for image in f:
        group = f[image]
        if not isinstance(group, h5py.Group):
            raise RuntimeError(f"Object at path {image} is of type {type(group)}, but \
            group is expected")

        crop_data = get_group_dataset(group, "1D_crop_data")
        widths = get_group_dataset(group, "width")
        heights = get_group_dataset(group, "height")

        for i in range(len(widths)):
            if widths[i] * heights[i] < 1000:
                continue
            crop = get_crop(crop_data, widths, heights, i)
            cv.imwrite(f"./Results/Crops_deconv/{str(image)}_{i}.png", crop)

