import numpy as np
import os
import time
from threading import Thread
import cv2 as cv

from multiprocessing import Process, Queue
from .logger import Logger
from .producer_functional import produce
from .consumer_functional import consume
from .utils import print_message


def filter_files(path):
    files = []
    for file in os.listdir(path):
        # filter here
        files.append(os.path.join(path, file))
    return files


def status_update(path: str, n_files: int, app):
    start = time.perf_counter()
    last_update = 0
    while last_update != 100:
        if os.path.isdir(os.path.join(path, "Data")):
            p = int(len(os.listdir(os.path.join(path, "Data"))) / n_files * 100)
            if p // 10 * 10 > last_update:
                print_message(app, f"{p//10 * 10}% done")
                last_update = p // 10 * 10
        time.sleep(1)
    duration = time.perf_counter() - start
    print_message(
        app, f"Total time: {duration}, Avg time per img: {duration / n_files}"
    )


def compute_mask_radius(files, offset: int = 0):
    radia = []
    for file in files:
        img = cv.imread(file, cv.IMREAD_GRAYSCALE)
        scale = img.shape[0] / 1000
        img = cv.blur(img, (111, 111))
        bigger_img = (np.random.sample((2000, 2000)) * 125).astype(np.uint8)
        bigger_img[500:1500, 500:1500] = cv.resize(img, (1000, 1000))

        img = bigger_img
        center = (img.shape[0] // 2, img.shape[1] // 2)

        def p(r):
            if r <= 0:
                return 0
            mask = np.zeros(img.shape, dtype=np.uint8)
            cv.circle(mask, center, r, 255, -1)
            return np.sum(cv.bitwise_and(img, mask)) / r

        step_size = 100
        p_old = 0
        r = 100

        while step_size > 0:
            p_up = p(r + step_size)
            p_down = p(r - step_size)
            if p_up > p_old:
                r += step_size
                p_old = p_up
            elif p_down > p_old:
                r -= step_size
                p_old = p_down
            else:
                step_size //= 2

        radia.append(int(r * scale) - offset)

    return min(radia)


def run_segmenter(
    source_folder: str,
    save_crops: bool,
    save_marked_imgs: bool,
    min_area_to_segment: float,
    min_area_to_save: float,
    save_path: str,
    equalize_hist: bool,
    resize: bool,
    clear_save_path: bool,
    bg_size: int,
    max_threads: int,
    n_sigma: float,
    n_cores: int,
    mask_imgs: bool,
    mask_radius_offset: int,
    app=None,
):
    files = filter_files(source_folder)
    files.sort(key=lambda x: float(os.path.basename(x).split("_")[0].split("-")[1]))    # sort after time
    files = files[:500]

    logger = Logger(
        save_crops,
        save_marked_imgs,
        min_area_to_segment,
        min_area_to_save,
        save_path,
        source_folder,
        equalize_hist,
        clear_save_path,
    )

    start = time.perf_counter()
    print_message(app, "Start segmenting")

    mask_radius = 0
    if mask_imgs:
        mask_radius = compute_mask_radius(files[:10], mask_radius_offset)
        print_message(app, f"Mask radius is: {mask_radius}")

    processes: list[Process] = []
    split_steps = len(files) // (n_cores // 2)
    for i in range(n_cores // 2):
        queue = Queue(15)
        upper_limit = (i + 1) * split_steps if i < n_cores // 2 - 1 else len(files)
        p1 = Process(
            target=produce,
            args=(
                bg_size,
                files[i * split_steps : upper_limit],
                resize,
                max_threads,
                queue,
                mask_imgs,
                mask_radius,
            ),
        )
        p2 = Process(target=consume, args=(queue, bg_size, n_sigma, logger))
        processes.append(p1)
        processes.append(p2)

    t = Thread(
        target=status_update,
        args=(
            os.path.join(save_path, os.path.basename(source_folder)),
            len(files),
            app,
        ),
    )
    t.start()

    for p in processes:
        p.start()

    for p in processes:
        p.join()

    t.join()
