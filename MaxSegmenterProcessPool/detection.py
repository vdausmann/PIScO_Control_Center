import cv2 as cv
import numpy as np
import os
import time
import csv

from multiprocessing import Queue
from MaxSegmenterProcessPool.process_pool import ProcessPool
from dataclasses import dataclass
#from tqdm import tqdm


@dataclass
class DetectionSettings:
    data_path: str
    crop_path: str
    mask_path: str
    img_path: str
    min_area_to_save: float
    min_area_to_segment: float
    n_sigma: float
    save_bb_image: bool
    save_crops: bool
    equalize_hist: bool
    resize: bool
    clear_save_path: bool
    mask_img: bool
    mask_radius: int


def save_crop_data(path, data):
    with open(path, "w", newline="") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerows(data)


def detect_on_img(input, settings: DetectionSettings, mask: np.ndarray, index=0):
    corrected, cleaned, mean_raw, fn = input
    if mean_raw[1]>2:
        #print(fn)
        # hier bild maskieren
        color = cv.cvtColor(cleaned, cv.COLOR_GRAY2BGR)
        #cleaned = cv.resize(cleaned, (2560, 2560))

        if settings.mask_img:
            mean = np.mean(corrected[np.where(mask == 255)])
            std = np.std(corrected[np.where(mask == 255)])
            corrected[np.where(mask < 255)] = 0
        else:
            mean = np.mean(corrected)
            std = np.std(corrected)   

        c = 2 #add small constant value for empty images.

        thresh = cv.threshold(
            corrected,
            #mean + settings.n_sigma * std +c,
            10,#fixed value now since images are very similar in color
            255,
            cv.THRESH_BINARY,
        )[1]
        thresh = thresh.astype(np.uint8)

        cnts, hierachy = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)#[0]
        #cnts, hierachy = cv.findContours(dilated_image, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)#[0]
        mask = np.zeros_like(thresh, dtype=np.uint8)

        areas = np.array([cv.contourArea(cnt) for cnt in cnts])
        if settings.resize:
            areas *= 4

        bounding_boxes = [cv.boundingRect(cnt) for cnt in cnts]
        # save center position and match bounding box to full width image
        bounding_boxes = np.array(
            [np.array((x + w / 2, y + h / 2, w, h)) for (x, y, w, h) in bounding_boxes]
        )
        if settings.resize:
            bounding_boxes *= 2

        crop_data = []
        c = 0
        for i, cnt in enumerate(cnts):
            if areas[i] < settings.min_area_to_segment:
                continue

            crop_fn = os.path.join(settings.crop_path, f"{fn[:-4]}_{c}.png")
            mask_fn = os.path.join(settings.mask_path, f"{fn[:-4]}_{c}.png")

            # if settings.save_bb_image:
            #     cv.drawContours(color, [cnt], -1, (0, 255, 0), 2)

            x, y, w, h = bounding_boxes[i]

            if areas[i] > settings.min_area_to_save:
                #mask = np.zeros_like(cleaned, dtype=np.uint8)
                crop_data.append([c, os.path.basename(crop_fn),mean_raw[0],mean_raw[1],mean,std, areas[i], x, y, w, h, 1])

                x = int(x - w / 2)
                y = int(y - h / 2)
                h = int(h)
                w = int(w)

                if settings.save_crops:
                    crop = cleaned[y : y + h, x : x + w]
                    cv.drawContours(mask,[cnt],-1,(255), thickness=cv.FILLED)                    
                    c_mask = mask[y : y + h, x : x + w]
                    crop_mask = np.where(c_mask == 255, crop, 255)
                    
                    cv.imwrite(crop_fn, crop_mask)#now only the object is saved and not objects close to it
                    cv.imwrite(mask_fn, c_mask)
            else:
                crop_data.append([c, os.path.basename(mask_fn),mean_raw[0],mean_raw[1],mean,std, areas[i], x, y, w, h, 0])

            c += 1

        if settings.save_bb_image:
            color = cv.resize(color, (1280, 1280))
            cv.imwrite(os.path.join(settings.img_path, fn), color)
            
            #cleaned = cv.resize(cleaned, (512, 512))
            # Create a mask from the thresholded image
            #thresh = np.where(thresh == 255, cleaned, 255).astype(np.uint8)

            # Create a white canvas with the same size as the original image
            #white_canvas = np.ones_like(cleaned)*255

            # Apply the mask to the original image
            #thresh = cv.bitwise_and(cleaned, white_canvas, mask=mask)
            #thresh = cv.bitwise_and(cleaned, mask=cv.bitwise_not(thresh))
            #cleaned = cv.resize((1000,1000), cleaned)
            #cv.imwrite(os.path.join(settings.img_path, 'cleaned', fn), cleaned)
            #cv.imwrite(os.path.join(settings.img_path, 'thresh_'+fn), thresh)

        save_crop_data(os.path.join(settings.data_path, fn[:-4] + ".csv"), crop_data)
    else:
        crop_data = []
        crop_data.append(['corrupt', os.path.basename(fn), 0, 0, 0, 0, 0, 0])
        save_crop_data(os.path.join(settings.data_path, fn[:-4] + ".csv"), ['corrupt image!'])


def run_detection(input: Queue, settings: DetectionSettings, n_cores, n_imgs, running):
    shape = (2560, 2560)
    if settings.resize:
        shape = (2560, 2560)
    mask = np.zeros(shape, dtype=np.uint8)
    if settings.mask_img:
        cv.circle(
            mask,
            (int(mask.shape[0] / 2), int(mask.shape[1] / 2)),
            settings.mask_radius,
            255,
            -1,
        )
    pool = ProcessPool(
        lambda input, index: detect_on_img(input, settings, mask, index),
        running,
        10,
    )
    pool.start(n_cores,'detection')
    for i in range(n_imgs):
        task = input.get()
        pool.add_task(task)
        print(i, task[-1]) #print filenames

    pool.stop(slow=True)

    while pool.is_running():
        print('.')
        time.sleep(1)

    print("detection finished")
