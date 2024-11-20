import os
import csv
import threading
import time
import subprocess
import cv2 as cv
import time
import uuid
from exif import Image as exIm
import hashlib

from PIL import Image ,ImageFile, ImageOps
ImageFile.LOAD_TRUNCATED_IMAGES = True
from PIL.PngImagePlugin import PngImageFile, PngInfo

from exif import Image as exIm

from datetime import datetime

import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from MaxSegmenter.MaxSegmenterModule import run_segmenter
from PISCO_DataGenerator import generate_matrix

#SAVE_FOLDER = "/Images/SO298/"
SAVE_FOLDER = "/home/pisco-controller/SO298/"

yaml_Lock=threading.Lock()


# def convert_img(filepath: str, compression_quality=85):
#     parent_folder = os.path.dirname(filepath)
#     fn = os.path.basename(filepath)
#     jpg_folder = os.path.join(parent_folder, "JPG")
#     png_folder = os.path.join(parent_folder, "PNG")
#     os.makedirs(jpg_folder, exist_ok=True)
#     os.makedirs(png_folder, exist_ok=True)

#     try:
#         img = cv.imread(filepath, cv.IMREAD_GRAYSCALE)
#         cv.imwrite(
#             os.path.join(jpg_folder, fn[:-3] + "jpg"),
#             img,
#             [cv.IMWRITE_JPEG_QUALITY, compression_quality],
#         )
#         cv.imwrite(os.path.join(png_folder, fn[:-3] + "png"), img)
#         cv.im
#     except:
#         pass
#     #os.remove(filepath)

""" def convert_img(filebatch: list, compression_quality=85):
    for filepath in filebatch:
        parent_folder = os.path.dirname(filepath)
        fn = os.path.basename(filepath)
        jpg_folder = os.path.join(parent_folder, "JPG")
        png_folder = os.path.join(parent_folder, "PNG")
        os.makedirs(jpg_folder, exist_ok=True)
        os.makedirs(png_folder, exist_ok=True)

        try:
            img = cv.imread(filepath, cv.IMREAD_GRAYSCALE)
            cv.imwrite(
                os.path.join(jpg_folder, fn[:-3] + "jpg"),
                img,
                [cv.IMWRITE_JPEG_QUALITY, compression_quality],
            )
            cv.imwrite(os.path.join(png_folder, fn[:-3] + "png"), img)
            cv.im
        except:
            pass
    #os.remove(filepath) """

# def convert_imgs(files: list[str]):
#     max_threads = 10
#     for file in files:
#         while len(threading.enumerate())>max_threads:
#             time.sleep(0.1)
#         threading.Thread(target=convert_img, args=(file,)).start()

""" def convert_imgs(files: list[str]):
    imgpthread=len(files)/10
    i=0
    x=0
    for i in range (10):
        i=i+1
        filebatch=[]
        for file in files:
            x=x+1
            if (x>imgpthread *(x-1) and x<imgpthread *x ):
                filebatch.append(file)
        threading.Thread(target=convert_img, args=(filebatch,)).start() """

def convert_img(filepath: str, metadataframe, compression_quality=85):
    parent_folder = os.path.dirname(filepath)
    fn = os.path.basename(filepath)
    [newdirname,newimgname,date,press]=metadataframe.get_filename(filepath)
   
    jpg_folder = os.path.join(os.path.dirname(parent_folder), newdirname + "_jpg")
    
    png_folder = os.path.join(os.path.dirname(parent_folder), newdirname + "_png")
    os.makedirs(jpg_folder, exist_ok=True)
    os.makedirs(png_folder, exist_ok=True)

    try:
        t1=time.time()
        targetImage = Image.open(filepath)
        metadata = PngInfo()
        uuid4_png=str(uuid.uuid4())        
        metadata.add_text("ImageUniqueID",uuid4_png)

        targetImage.save(os.path.join(png_folder, newimgname + ".png"), pnginfo=metadata,compress_level=3)
        #sha256_hash_png = hashlib.sha256()
        # with open(os.path.join(png_folder, newimgname + ".png"),"rb") as f:
        #     # Read and update hash string value in blocks of 4K
        #     for byte_block in iter(lambda: f.read(4096),b""):
        #         sha256_hash_png.update(byte_block)
        #     sha256_hash_png.hexdigest()
        t2=time.time()
        #print(f"PIL Time : {t2-t1}")

        t1=time.time()
        imgg = cv.imread(filepath, cv.IMREAD_GRAYSCALE)
        cv.imwrite(
            os.path.join(jpg_folder, newimgname + ".jpg"),
            imgg,
            [cv.IMWRITE_JPEG_QUALITY, compression_quality],
        )
        #write UUID to image meta data
        with open(os.path.join(jpg_folder, newimgname + ".jpg"), 'rb') as img_file:
            img = exIm(img_file)
            uuid4_jpg=str(uuid.uuid4())   
            img.image_unique_id=uuid4_jpg
            
        with open(os.path.join(jpg_folder, newimgname + ".jpg"), 'wb') as img_file2:
            img_file2.write(img.get_file())
        # sha256_hash_jpg = hashlib.sha256()
        # with open(os.path.join(jpg_folder, newimgname + ".jpg"),"rb") as f:
        #     # Read and update hash string value in blocks of 4K
        #     for byte_block in iter(lambda: f.read(4096),b""):
        #         sha256_hash_jpg.update(byte_block)
        #     sha256_hash_jpg.hexdigest()    
        t2=time.time()   
        #print(f"CV JPG Time : {t2-t1}") 

        # t1=time.time()
        # cv.imwrite(os.path.join(png_folder, newimgname + ".png"), imgg)
        # t2=time.time()
        # print(f"CV PNG Time : {t2-t1}") 
        
        sha256_hash_jpg=0
        sha256_hash_png=0
        ## yaml
        t1=time.time()
        with yaml_Lock:
            metadataframe.write_meta(jpg_folder,newimgname + ".jpg",uuid4_jpg,date,press,sha256_hash_jpg)        
            metadataframe.write_meta(png_folder,newimgname + ".png",uuid4_png,date,press,sha256_hash_png)
        t2=time.time()  
        #print(f"Yaml Time : {t2-t1}")   
        
        # t1=time.time()
        # metadataframe.write_meta(jpg_folder,newimgname + ".jpg",uuid4_jpg,date,press,sha256_hash_jpg)
        
        # metadataframe.write_meta(png_folder,newimgname + ".png",uuid4_png,date,press,sha256_hash_png)  
        
        # t2=time.time()  
        # print(f"Yaml Time : {t2-t1}") 

    except:
        print("Convert Error")
        pass
    # os.remove(filepath)


def convert_imgs(files: list[str], metadataframe):
    max_threads = 12
    
    # parent_folder = os.path.dirname(files[0])
    # [newdirname,newimgname,date,press]=metadataframe.get_filename(files[0])
   
    # jpg_folder = os.path.join(os.path.dirname(parent_folder), newdirname + "_jpg")
    
    # png_folder = os.path.join(os.path.dirname(parent_folder), newdirname + "_png")
    # os.makedirs(jpg_folder, exist_ok=True)
    # os.makedirs(png_folder, exist_ok=True)
    yaml_Lock=threading.Lock()
    
    t1=time.time()
    for file in files:
        while len(threading.enumerate())>max_threads:
            time.sleep(0.1)
        threading.Thread(target=convert_img, args=(file, metadataframe)).start()
    t2=time.time() 
    print(f"Convert Time : {t2-t1}")    


def get_csv_filename(path: str = ""):
    t = datetime.now()
    fn = f"{t.year}_{t.month}_{t.day}_{t.hour}.csv"
    return os.path.join(path, fn)


def generate_csv():
    proc = subprocess.Popen(
        "exec sshpass -p "
        "pw19"
        " ssh plankdeep@192.168.0.1 '/home/plankdeep/plankdeep/ladestart.sh'",
        shell=True,
        stdout=subprocess.PIPE,
    )


def download_csv(fn: str):
    process = subprocess.Popen(
        "exec  sshpass -p "
        "pw19"
        f" scp  plankdeep@192.168.0.1:/home/plankdeep/plankdeep/Filelists/filelist.csv {fn}",
        shell=True,
        stdout=subprocess.PIPE,
    )


def move_imgs():
    process = subprocess.Popen(
        "exec  sshpass -p "
        "pw19"
        #home/pisco-controller/SO298
        #" rsync -r plankdeep@192.168.0.1:/images/ /home/pisco-controller/SO298/",
        #" rsync -r plankdeep@192.168.0.1:/images/ /home/pisco-controller/SO298/",
        " rsync --remove-source-files -r plankdeep@192.168.0.1:/images/ /home/pisco-controller/SO298/",
        #" rsync --remove-source-files -r plankdeep@192.168.0.1:/images/ /Images/SO298/",
        #" rsync --remove-source-files -r plankdeep@192.168.0.1:/images/ /home/plankton/Documents/destfold/",
        shell=True,
        stdout=subprocess.PIPE,
    )


def shutdown_camera():
    proc = subprocess.Popen(
        "exec sshpass -p "
        "pw19"
        " ssh plankdeep@192.168.0.1 'sudo -S <<< pw19 poweroff'",
        shell=True,
        stdout=subprocess.PIPE,
    )


def get_files(csv_file: str):
    with open(csv_file, "r") as f:
        data = list(csv.reader(f, delimiter=","))
    data = [os.path.join(SAVE_FOLDER, fn[0]) for fn in data]
    return data


def check_img_download_finished(missing_files: list[str]):
    still_missing = []
    for file in missing_files:
        if not os.path.isfile(file):
            still_missing.append(file)
    return still_missing


def get_profile_folders(csv_file: str, step_width: int = 100):
    files = get_files(csv_file)
    profiles = []
    i = 0
    while i < len(files):
        file = files[i]
        profile = os.path.dirname(file)
        if not profile in profiles:
            profiles.append(profile)
        i += step_width
    profiles = [os.path.join(profile, "PNG") for profile in profiles]
    return profiles


def update_csv(csv_file: str):
    imgs = []
    for dirpath, dirnames, filenames in os.walk(SAVE_FOLDER):
        if os.path.basename(dirpath) in ["PNG", "JPG"]:
            continue
        for fn in filenames:
            if fn[-3:] == "tif":
                imgs.append([os.path.join(os.path.relpath(dirpath, SAVE_FOLDER), fn)])

    print(f"{len(imgs)} imgs found")
    with open(csv_file, "w") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerows(imgs)


def print_message(app, message: str):
    if app is None:
        print(message)
    else:
        app.print(message)


def main(
    save_path: str,
    save_crops: bool,
    save_marked_imgs: bool,
    min_area_to_segment: float,
    min_area_to_save: float,
    equalize_hist: bool,
    resize: bool,
    clear_save_path: bool,
    bg_size: int,
    max_threads: int,
    n_sigma: float,
    n_cores: int,
    mask_imgs: bool,
    mask_radius_offset: int,
    size_of_depth_bins: float,
    size_of_area_bins: float,
    only_saved: bool,
    metadataframe,
    app=None,
):
    print_message(app, "Full pipeline started...")
    # start script to generate csv
    generate_csv()
    time.sleep(15)

    # start script to get the csv
    csv_fn = get_csv_filename("/home/pisco-controller/Desktop/PISCO_Software/File_csv/")
    try:
        os.remove(csv_fn)
    except FileNotFoundError:
        pass
    download_csv(csv_fn)
    while not os.path.isfile(csv_fn):
        time.sleep(0.5)
    print_message(app, f"Found csv file: {csv_fn}")
    # move imgs
    move_imgs()
    print_message(app, "Moving files...")
    missing_files = get_files(csv_fn)
    while len(missing_files) > 0:
        missing_files = check_img_download_finished(missing_files)
        print_message(app, f"Missing files: {len(missing_files)}")
        time.sleep(5)
    print_message(app, "Finished moving files")

    # shutdown camera
    shutdown_camera()

    # update csv
    update_csv(csv_fn)
    print_message(app, "Updated csv")

    # convert imgs
    # erstelle yaml
    print_message(app, "Converting images...")
    convert_imgs(get_files(csv_fn), metadataframe)
    print_message(app, "All images converted")

    profiles = get_profile_folders(csv_fn)
    for profile in profiles:
        print_message(app, f"Start segmenting {profile}")
        save_folder = os.path.join(
            save_path,
            os.path.dirname(
                #os.path.relpath(profile, "/home/plankton/Documents/destfold")
                os.path.relpath(profile, "/home/pisco-controller/SO298")
                #os.path.relpath(profile, "/Images/SO298")
            ),
        )
        # segment imgs
        run_segmenter(
            source_folder=profile,
            save_crops=save_crops,
            save_marked_imgs=save_marked_imgs,
            min_area_to_segment=min_area_to_segment,
            min_area_to_save=min_area_to_save,
            save_path=save_folder,
            equalize_hist=equalize_hist,
            resize=resize,
            clear_save_path=clear_save_path,
            bg_size=bg_size,
            max_threads=max_threads,
            n_sigma=n_sigma,
            n_cores=n_cores,
            mask_imgs=mask_imgs,
            mask_radius_offset=mask_radius_offset,
            app=app,
        )
        generate_matrix.compute_matrix(
            os.path.join(save_folder, "PNG"),
            size_of_depth_bins,
            size_of_area_bins,
            only_saved=only_saved,
        )

        print_message(app, f"Finished segmenting {profile}")


if __name__ == "__main__":
    main(
        
        save_path="/home/pisco-controller/SO298-Segmentation",
        #save_path="/Images/SO298-Segmentation",
        save_crops=True,
        save_marked_imgs=True,
        min_area_to_segment=100,
        min_area_to_save=100,
        equalize_hist=True,
        resize=False,
        clear_save_path=True,
        bg_size=5,
        max_threads=12,
        n_sigma=1.5,
        n_cores=6,
        mask_imgs=True,
        mask_radius_offset=100,
        size_of_depth_bins=5,
        size_of_area_bins=1000,
        only_saved=False,
    )
