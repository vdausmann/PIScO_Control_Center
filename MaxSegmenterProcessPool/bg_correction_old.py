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
        # bg = np.max([img[0] for img in input.images[start : start + n_bg_imgs]], axis=0)
        bg = np.max(bg_imgs, axis=0)
        #im_list = [img[0] for img in input.images[start : start + n_bg_imgs]]
        #bg = np.max(im_list, axis=0)
        #bg[np.where(bg>np.mean(bg[int(2560/3):int(2560/3*2),int(2560/3):int(2560/3*2)])+10,)] = np.mean(bg[int(2560/3):int(2560/3*2),int(2560/3):int(2560/3*2)])

        correct_img = cv.absdiff(img, bg)
        cleaned_img = cv.bitwise_not(correct_img)
        cleaned_img[np.where(cleaned_img >= 250)] = np.mean(cleaned_img)
        
        # # Define the radius of the rolling ball
        # radius = 3

        # # Create the rolling ball kernel
        # rolling_ball_kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (2*radius+1, 2*radius+1))

        # # # Perform morphological opening using the rolling ball kernel
        # # cleaned_img= cv.morphologyEx(cleaned_img, cv.MORPH_OPEN, rolling_ball_kernel)
        # # Define the radius for local background estimation (should be at least the size of the largest object)
        # radius = 200

        # # Create the rolling ball kernel (large circular kernel for background estimation)
        # background_kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (2*radius+1, 2*radius+1))

        # # Compute the local background using morphological opening
        # local_background = cv.morphologyEx(cleaned_img, cv.MORPH_OPEN, background_kernel)

        # # Subtract the local background from the original image
        # cleaned_img = cv.subtract(cleaned_img, local_background)
        # Define the radius for local background estimation
        # radius = 60

        # # Calculate the local mean using a rolling ball-like approach
        # local_mean = uniform_filter(cleaned_img, size=2*radius+1)

        # # Subtract the local mean from the original image
        # background_removed = cv.bitwise_not(cv.absdiff(cleaned_img , local_mean))
        # cleaned_img = background_removed
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
