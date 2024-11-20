import os
import time
import csv
import numpy as np


def get_crop_data(profile_path: str):
    crop_data = []
    path = os.path.join(profile_path, "Data")
    files = os.listdir(path)
    max_depth, max_area = 0, 0
    for file in files:
        if file != "imgdata.csv":
            splitted = file.split("_")
            depth = 0
            for split in splitted:
                if "bar" in split:
                    depth = (float(split[: split.index("b")]) - 1) / 0.0981
            if depth > max_depth:
                max_depth = depth
            with open(os.path.join(path, file), "r") as f:
                data = list(csv.reader(f, delimiter=","))
                if len(data) > 1:
                    crop_data.append([])
                    for row in data[1:]:
                        crop_data[-1].append([])
                        crop_data[-1][-1].append(depth)
                        filename = f"{row[1][:-4]}_{row[0]}.jpg"
                        crop_data[-1][-1].append(filename)  # filename
                        area = float(row[2])
                        if area > max_area:
                            max_area = area
                        crop_data[-1][-1].append(area)  # area
                        crop_data[-1][-1].append(int(row[-1]))  # saved

    crop_data.sort(key=lambda x: x[0])
    return crop_data, max_depth, max_area


Y_OFFSET = 1
X_OFFSET = 4

PROFILE_ID_INDEX = 0
TIME_INDEX = 1
DEPTH_BINS_INDEX = 2
IMGS_PER_DEPTH_BIN_INDEX = 3


def find_crop(depth, size_of_depth_bins, area, size_of_area_bins, crop_data):
    c = 0
    for file in crop_data:
        depth_index = int(file[0][0] // size_of_depth_bins)
        if depth_index * size_of_depth_bins == depth:
            for row in file:
                area_index = int(row[2] // size_of_area_bins)
                if area_index * size_of_area_bins == area:
                    c += 1
                    print(row[1], row[0], row[2])
                elif area_index * size_of_area_bins > area:
                    print("r", row[0], row[2])
        elif depth_index * size_of_depth_bins > depth:
            break

    print(c)


def save_mat(filename: str, mat: list[list]):
    with open(filename, "w") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerows(mat)


def compute_matrix(
    profile_path: str,
    size_of_depth_bins: float,
    size_of_area_bins: float,
    only_saved: bool,
):
    crop_data, max_depth, max_area = get_crop_data(profile_path)
    depth_bins = []
    matrix: list[list[float | str]] = [
        [0 for _ in range(int(max_area // size_of_area_bins + X_OFFSET + 1))]
        for _ in range(int(max_depth // size_of_depth_bins + Y_OFFSET + 1))
    ]
    # matrix = np.zeros(
    # (
    # int(max_depth // size_of_depth_bins + Y_OFFSET + 1),
    # int(max_area // size_of_area_bins + X_OFFSET + 1),
    # )
    # )

    for row in range(len(matrix) - Y_OFFSET):
        matrix[row + Y_OFFSET][PROFILE_ID_INDEX] = os.path.basename(profile_path)
        matrix[row + Y_OFFSET][TIME_INDEX] = time.time()
        matrix[row + Y_OFFSET][DEPTH_BINS_INDEX] = row * size_of_depth_bins

    # headers
    matrix[0][PROFILE_ID_INDEX] = "Profile ID"
    matrix[0][TIME_INDEX] = "Timestamp"
    matrix[0][DEPTH_BINS_INDEX] = "Depth bins in m"
    matrix[0][IMGS_PER_DEPTH_BIN_INDEX] = "Images in depth bin"

    for col in range(len(matrix[0]) - X_OFFSET):
        matrix[0][col + X_OFFSET] = f"Number particles in {col * size_of_area_bins}"

    for file in crop_data:
        depth_index = int(file[0][0] // size_of_depth_bins) + Y_OFFSET
        matrix[depth_index][IMGS_PER_DEPTH_BIN_INDEX] += 1  # type: ignore
        for row in file:
            if not only_saved or row[3] == 1:
                area_index = int(row[2] // size_of_area_bins) + X_OFFSET
                matrix[depth_index][
                    area_index
                ] += 1  # particle count in depth and area bin  #type: ignore

    # np.savetxt("mat.csv", matrix, delimiter=",")
    save_mat(os.path.join(profile_path, "mat.csv"), matrix)


if __name__ == "__main__":
    # data, area, depth = get_crop_data("/home/tim/Documents/Arbeit/Results/TestMax/M181Test")
    # print(area, depth)
    # for d in data:
    #     print(d[0][0], d[0][0] // 5)

    compute_matrix("C:/Users/timka/Documents/Arbeit/Results/M181Test/", 5, 5000, True)
    # find_crop(0, 5, 0, 10000, data)
