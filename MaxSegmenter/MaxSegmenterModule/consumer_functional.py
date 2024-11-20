import cv2 as cv
import numpy as np
import threading
import time
from multiprocessing import Queue
from .utils import ProducerData, ConsumerData
from .logger import Logger


def find_objects(incoming_message: ProducerData, n_sigma: float, logger: Logger):
    corrected = incoming_message.corrected_img
    cleaned_img = cv.absdiff(corrected, incoming_message.original_img_mean)  # type: ignore

    thresh = cv.threshold(
        corrected,
        np.mean(corrected) + n_sigma * np.std(corrected),
        255,
        cv.THRESH_BINARY,
    )[1]

    cnts = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)[0]
    areas = [cv.contourArea(cnt) for cnt in cnts]
    if incoming_message.resized:
        areas *= 4
    bounding_boxes = [cv.boundingRect(cnt) for cnt in cnts]
    # possible resizing for bounding boxes

    message = ConsumerData(
        incoming_message.filename,
        incoming_message.read_at,
        time.perf_counter(),
        cleaned_img,
        bounding_boxes,
        areas,
    )
    logger.save_results(message)


def consume(receiver_queue: Queue, max_threads: int, n_sigma: float, logger: Logger):
    while True:
        message = receiver_queue.get()

        message = ProducerData(*message)
        if message.finished:
            break

        while len(threading.enumerate()) >= max_threads:
            time.sleep(0.01)
        threading.Thread(target=find_objects, args=(message, n_sigma, logger)).start()

    while len(threading.enumerate()) > 1:
        time.sleep(0.01)
