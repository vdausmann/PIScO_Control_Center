import time
import cv2 as cv
import numpy as np
import os

from MaxSegmenterProcessPool.process_pool import ProcessPool
from multiprocessing import Queue
from MaxSegmenterProcessPool.reader import ReaderOutput
from scipy.ndimage import uniform_filter


def is_ready(img_index: int, input: ReaderOutput, n_bg_imgs):
    start = (
        img_index
        if img_index + n_bg_imgs < len(input.images)
        else len(input.images) - n_bg_imgs
    )
    for i in range(start, start + n_bg_imgs):
        if input.images[i] is None:
            return False
    return True


def correct_img(
    img_index: int, input: ReaderOutput, output: Queue, n_bg_imgs: int, index=0
):
    n_bg_imgs *= 2
    while not is_ready(img_index, input, n_bg_imgs):
        time.sleep(0.1)
    img, fn = input.images[img_index]
    mean = np.mean(img)
    stdev = np.std(img)
    if stdev >2:
        start = (img_index if img_index + n_bg_imgs < len(input.images) else len(input.images) - n_bg_imgs)
        bg_imgs: list[np.ndarray] = []
        for i in range(1, n_bg_imgs):
            bg_imgs.append(
                np.min([input.images[start + i - 1][0], input.images[start + i][0]], axis=0)
            )
        bg = np.max(bg_imgs, axis=0)
        
        correct_img = cv.absdiff(img, bg)
        cleaned_img = cv.bitwise_not(correct_img)
        #fixing problem where very bright objects (plankton acts as lens?!) print through on following images: see mattermost board "Segmenter Problem: Durchdrucken großer/dunkler Objekte im MaxSegmenter"
        #cleaned_img[np.where(cleaned_img >= 250)] = np.mean(bg) 
        
        output.put((correct_img, cleaned_img, [mean,stdev], fn))
    else:
        print('found corrupt image: ', fn)

        output.put(([], [], [mean,stdev], fn))


def run_bg_correction(input: ReaderOutput, output: Queue, n_bg_imgs: int, running):
    pool = ProcessPool(
        lambda img_index, index: correct_img(
            img_index, input, output, n_bg_imgs, index
        ),
        running,
        -1,
    )
    pool.start(3,'bg_corr')
    #print(len(input.images))
    for i in range(len(input.images)):
        try:
            pool.add_task(i)
        except Exception as e:
            print(f"Exception when adding image {i} to bg correction pool: {e}")
    pool.stop(slow=True)

    # while pool.is_running():
    #     time.sleep(1)

    # print("Bg correction finished")
