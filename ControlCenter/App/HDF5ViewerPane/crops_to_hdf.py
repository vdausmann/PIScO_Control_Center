import numpy as np
import cv2 as cv
import math

def generate_crop_atlas(crops, tile_size=16, max_cols=100) -> tuple[np.ndarray, list]:
    """Packaging algorithm that creates one tiled image per source image with all crops."""
    meta = []

    # tiling:
    tiles = []
    tile_cols = []
    for crop in crops:
        c_h, c_w = crop.shape
        rows = math.ceil(c_h / tile_size)
        cols = math.ceil(c_w / tile_size)

        tiled_crop = np.zeros((rows * tile_size, cols * tile_size), dtype=np.uint8)
        tiled_crop[:c_h, :c_w] = crop
        tiles.append(tiled_crop)
        tile_cols.append(cols)

    tiles.sort(key=lambda x: x.shape[0], reverse=True)

    max_cols = max(max_cols, max(tile_cols)) * tile_size
    running_col = 0
    tile_rows = [[]]
    for tile in tiles:
        if running_col + tile.shape[1] >= max_cols:
            tile_rows.append([])
            running_col = 0
        running_col += tile.shape[1]
        tile_rows[-1].append(tile)

    atlas = []
    tile_row = 0
    for row in tile_rows:
        rows = max([tile.shape[0] for tile in row])
        atlas_tile = np.zeros((rows, max_cols), dtype=np.uint8)

        col = 0
        for tile in row:
            atlas_tile[:tile.shape[0], col: col + tile.shape[1]] = tile
            meta.append({"tile_rect": (col, tile_row, tile.shape[0], tile.shape[1])}) # x, y, w, h
            col += tile.shape[1]

        atlas.append(atlas_tile)
        tile_row += rows

    atlas = np.concatenate(atlas, 0)
    return atlas, meta
