import os
import cv2 as cv
import csv
import threading
import time



def convert_img(filepath: str, metadataframe, compression_quality=85):
    parent_folder = os.path.dirname(filepath)
    fn = os.path.basename(filepath)
    [newdirname,newimgname]=metadataframe.get_filename(filepath)
   
    jpg_folder = os.path.join(os.path.dirname(parent_folder), newdirname + "_jpg")
    
    png_folder = os.path.join(os.path.dirname(parent_folder), newdirname + "_png")
    os.makedirs(jpg_folder, exist_ok=True)
    os.makedirs(png_folder, exist_ok=True)

    try:
        img = cv.imread(filepath, cv.IMREAD_GRAYSCALE)
        cv.imwrite(
            os.path.join(jpg_folder, newimgname + ".jpg"),
            img,
            [cv.IMWRITE_JPEG_QUALITY, compression_quality],
        )
        cv.imwrite(os.path.join(png_folder, newimgname + ".png"), img)
        ## yaml
        metadataframe.write_meta(jpg_folder,newimgname + ".jpg")
        metadataframe.write_meta(png_folder,newimgname + ".png")
    except:
        pass
    # os.remove(filepath)


def convert_imgs(files: list[str], metadataframe):
    max_threads = 10
    for file in files:
        while len(threading.enumerate())>max_threads:
            time.sleep(0.1)
        threading.Thread(target=convert_img, args=(file, metadataframe)).start()