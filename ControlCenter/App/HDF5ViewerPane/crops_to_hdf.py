from os.path import isfile
import numpy as np
import cv2 as cv
import math
import os
import h5py
import json

from scipy.sparse import data
from Utils.types import Image
import pandas as pd

def generate_crop_atlas(crops: list[Image], metadata: dict[str, dict], tile_size=16, max_cols=100) -> np.ndarray:
    """Packaging algorithm that creates one tiled image per source image with all crops."""

    # tiling:
    tiles: list[Image] = []
    tile_cols = []
    for crop in crops:
        c_h, c_w = crop.data.shape
        rows = math.ceil(c_h / tile_size)
        cols = math.ceil(c_w / tile_size)

        tiled_crop = Image(crop.fname, np.zeros((rows * tile_size, cols * tile_size),
                                                dtype=np.uint8), crop.color_code)
        tiled_crop.data[:c_h, :c_w] = crop.data
        tiles.append(tiled_crop)
        tile_cols.append(cols)

    tiles.sort(key=lambda x: x.data.shape[0], reverse=True)

    max_cols = max(max_cols, max(tile_cols)) * tile_size
    running_col = 0
    tile_rows: list[list[Image]] = [[]]
    for tile in tiles:
        if running_col + tile.data.shape[1] >= max_cols:
            tile_rows.append([])
            running_col = 0
        running_col += tile.data.shape[1]
        tile_rows[-1].append(tile)

    atlas = []
    tile_row = 0
    for row in tile_rows:
        rows = max([tile.data.shape[0] for tile in row])
        atlas_tile = np.zeros((rows, max_cols), dtype=np.uint8)

        col = 0
        for tile in row:
            atlas_tile[:tile.data.shape[0], col: col + tile.data.shape[1]] = tile.data
            if not tile.fname in metadata:
                metadata[tile.fname] = {}
            metadata[tile.fname]["tile_data"] = {"x": col, "y": tile_row, "w": tile.data.shape[1],
                         "h": tile.data.shape[0]}
            col += tile.data.shape[1]

        if len(tile_rows) == 1 and col < max_cols * tile_size:
            atlas_tile = atlas_tile[:, :col]

        atlas.append(atlas_tile)
        tile_row += rows


    atlas = np.concatenate(atlas, 0)
    return atlas



def generate_crop_hdf_file(path_to_crop_images: str, path_to_crop_data: str,
                           hdf_output_file: str):
    # Assumes one crop data file per source image which is named like the source image.
    crop_data_files = [f for f in os.listdir(path_to_crop_data) if f.endswith(".csv")]
    crop_data_files.sort()
    
    with h5py.File(hdf_output_file, "w") as f:
        for data_file in crop_data_files:
            dataframe = pd.read_csv(os.path.join(path_to_crop_data, data_file), delimiter=",",
                                    header=None, index_col=False)

            crops = []
            meta = {}
            for i in range(dataframe.shape[0]):
                image_file = dataframe.iloc[i][1]
                if os.path.isfile(os.path.join(path_to_crop_images, image_file)):
                    crop_image = cv.imread(os.path.join(path_to_crop_images, image_file), cv.IMREAD_GRAYSCALE)
                    if crop_image is None:
                        continue
                    crop = Image(
                        image_file,
                        crop_image,
                        cv.IMREAD_GRAYSCALE
                        )
                    crops.append(crop)
                data_row = dataframe.loc[i]
                meta[image_file] = {
                        "bounding_box": {"x": data_row[2], "y": data_row[3],
                                         "w": data_row[4], "h": data_row[5]}
                        }
            if not crops:
                continue
            atlas = generate_crop_atlas(crops, meta)

            group = f.create_group(data_file[:-4])
            dataset = group.create_dataset("atlas", data=atlas, compression="gzip",
                                 compression_opts=4)
            dataset.attrs["type"] = "image"
            dataset.attrs["description"] = "Atlas of crops"

            meta_str = json.dumps(meta)
            dataset = group.create_dataset("metadata", data=meta_str)
            dataset.attrs["type"] = "dict"
            dataset.attrs["description"] = "Metadata of crops"


