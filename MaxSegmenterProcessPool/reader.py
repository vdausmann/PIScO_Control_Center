import cv2 as cv
import numpy as np
import time
import os
import threading
from MaxSegmenterProcessPool.process_pool import ProcessPool
from multiprocessing import Manager
from MaxSegmenterProcessPool.thread_pool import ThreadPool

from PIL import Image
#import torchvision.transforms.functional as TF



class ReaderOutput:
    def __init__(self, n_images, manager: Manager) -> None:
        self.lock = threading.Lock()
        self.images = manager.list([None for _ in range(n_images)])

    def add_output(self, img, fn, index):
        with self.lock:
            self.images[index] = (img, fn)


def read_img(output: ReaderOutput, input, thread_index=0):
    file, img_index = input
    fn = os.path.basename(file)
    # Check if the file size is 0 bytes
    if os.path.getsize(file) == 0:
        print(f'Thread {thread_index}: File {file}is an empty image file')
        return
    try:
        img = cv.imread(file, cv.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError(f"Thread {thread_index}: File {file} is not a valid image.")
        #if resize:
        img = cv.resize(img, (2560, 2560))
        output.add_output(img, fn, img_index)
    except Exception as e:
        print('...exception occurred:', e)
        


def run_reader(files, output: ReaderOutput, n_threads: int, resize:bool):
    pool = ThreadPool(lambda input, index: read_img(output, input, index), 100)
    pool.start(n_threads)
    for file in files:
        #print(f"Adding file {file} to reader pool")
        try:
            pool.add_task(file)
        except Exception as e:
            print(f"Exception when adding file {file} to reader pool: {e}")
        #print("Waiting for reader pool to finish")
    print('all files in batch added to reader pool')
    pool.stop(slow=True)

    # Für batchwise das untere auskommentieren, bessere Performance

    # while pool.is_running():
    #      time.sleep(1)

    # print("Reader finished")
