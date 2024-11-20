import cv2 as cv
import numpy as np
import threading
import os
import time
from .utils import ProducerData
from multiprocessing import Queue


def init_bg_imgs(
    files: list[str],
    resize: bool,
    bg_size: int,
    mask_imgs: bool,
    mask_radius: int,
):
    bg_imgs = []
    for file in files:
        # read img and check integrity
        img = cv.imread(file, cv.IMREAD_GRAYSCALE)
        if mask_imgs:
            mask = np.zeros(img.shape, dtype=np.uint8)
            cv.circle(
                mask, (img.shape[0] // 2, img.shape[1] // 2), mask_radius, 255, -1
            )
            img = cv.bitwise_and(img, mask)
        if resize:
            img = cv.resize(img, (2560, 2560))
        bg_imgs.append(img)
        if len(bg_imgs) == bg_size:
            break
    return bg_imgs



def process_img(
    index: int,
    bg_imgs: list[np.ndarray],
    filename: str,
    timestamp: float,
    sending_queue: Queue,
    resize: bool,
):
    img = bg_imgs[index]
    bg = np.max(bg_imgs, axis=0)
    corrected = cv.absdiff(img, bg)
    message = ProducerData(
        finished=False,
        filename=os.path.basename(filename),
        read_at=timestamp,
        corrected_img=corrected,
        original_img_mean=np.mean(
            img[
                int(img.shape[0] * 0.2) : int(img.shape[0] * 0.8),
                int(img.shape[0] * 0.2) : int(img.shape[0] * 0.8),
            ]
        ),  # type:ignore
        resized=resize,
    )
    sending_queue.put(message.get_tuple())


def produce(
    bg_size: int,
    files: list[str],
    resize: bool,
    max_threads: int,
    sending_queue: Queue,
    mask_imgs: bool,
    mask_radius: int,
):

    new_bg_img_index = 0
    img_to_process_index = 0
    bg_imgs = init_bg_imgs(files, resize, bg_size, mask_imgs, mask_radius)

    for i in range(bg_size // 2, len(files) + bg_size // 2):
        timestamp = time.perf_counter()
        # new bg:
        if i >= bg_size and i <= len(files) - bg_size:
            file = files[i]
            # read img and check integrity
            img = cv.imread(file, cv.IMREAD_GRAYSCALE)
            if mask_imgs:
                mask = np.zeros(img.shape, dtype=np.uint8)
                cv.circle(
                    mask, (img.shape[0] // 2, img.shape[1] // 2), mask_radius, 255, -1
                )
                img = cv.bitwise_and(img, mask)
            if resize:
                img = cv.resize(img, (2560, 2560))
            bg_imgs[new_bg_img_index] = img
            new_bg_img_index += 1
            new_bg_img_index = new_bg_img_index if new_bg_img_index < bg_size else 0

        while len(threading.enumerate()) >= max_threads:
            time.sleep(0.01)
        threading.Thread(
            target=process_img,
            args=(
                img_to_process_index,
                bg_imgs.copy(),
                files[i - bg_size // 2],
                timestamp,
                sending_queue,
                resize,
            ),
        ).start()
        img_to_process_index += 1
        img_to_process_index = (
            img_to_process_index if img_to_process_index < bg_size else 0
        )

    while len(threading.enumerate()) > 2:
        time.sleep(0.01)
    message = ProducerData(finished=True)
    sending_queue.put(message.get_tuple())
