import tkinter as tk
from tkinter.messagebox import showinfo
import customtkinter as ctk
from threading import Thread
import time

import os
import csv
import threading
import time
import subprocess
import cv2 as cv
import time
import uuid
from exif import Image as exIm

from PIL import Image ,ImageFile, ImageOps
ImageFile.LOAD_TRUNCATED_IMAGES = True
from PIL.PngImagePlugin import PngImageFile, PngInfo

from exif import Image as exIm

from datetime import datetime

#from metadata_frame import MetadataFrame.settings

import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from PISCO_Pipeline import pipeline
from PISCO_Pipeline import single_pipe
#from MaxSegmenter import MaxSegmenterModule
from PISCO_DataGenerator import generate_matrix



class Sidebar(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.master = app
        # start full pipeline
        self.pipeline_bt = ctk.CTkButton(
            self, text="Process Profile (Auto)", command=self.start_pipeline
        )
        self.pipeline_bt.pack(padx=5, pady=5)

        # start full pipeline
        self.pipeline_bt = ctk.CTkButton(
            self, text="Process downloaded Profile", command=self.start_single_pipe
        )
        self.pipeline_bt.pack(padx=5, pady=5)

        # start full segmenter
        self.segmenter_bt = ctk.CTkButton(
            self, text="Start segmenter", command=self.start_segmenter
        )
        self.segmenter_bt.pack(padx=5, pady=5)

        # get imgs
        self.get_imgs_bt = ctk.CTkButton(self, text="Get imgs", command=self.get_imgs)
        self.get_imgs_bt.pack(padx=5, pady=5)

        # shut of camera
        self.shut_off_bt = ctk.CTkButton(
            self, text="Shut off camera", command=self.shut_off_camera
        )
        self.shut_off_bt.pack(padx=5, pady=5)

        # compute data
        self.compute_data_bt = ctk.CTkButton(
            self, text="Compute data", command=self.compute_data
        )
        self.compute_data_bt.pack(padx=5, pady=5)

        # save settings
        ctk.CTkButton(self, text="Save Settings", command=self.master.save_settings).pack(padx=5, pady=5)  # type: ignore

        # help button
        ctk.CTkButton(self, text="Help", command=self.help).pack(padx=5, pady=5)
        # quit button
        ctk.CTkButton(self, text="Quit", command=master.quit).pack(padx=5, pady=5)

    def compute_data(self):
        settings = self.master.evaluation_frame.get_settings()  # type: ignore
        self.master.print(str(settings))  # type: ignore
        Thread(
            target=generate_matrix.compute_matrix,
            args=(
                settings["profile_path"],
                float(settings["size_of_depth_bins"]),
                float(settings["size_of_area_bins"]),
                settings["only_saved"],
            ),
        ).start()

    def shut_off_camera(self):
        Thread(target=pipeline.shutdown_camera()).start()
        self.master.print("Camera shut off")

    def get_imgs(self):
        print("Get imgs")
        compression_quality=85
        filepath=("/home/pisco-controller/SO298/20231124/20231124-1101/20231124-11011101_000.969bar_23.61C.tif")
        parent_folder = os.path.dirname(filepath)
        fn = os.path.basename(filepath)
        [newdirname,newimgname]=[parent_folder,"test.tiff"]
    
        jpg_folder = os.path.join(os.path.dirname(parent_folder), newdirname + "_jpg")
        print(jpg_folder)
        png_folder = os.path.join(os.path.dirname(parent_folder), newdirname + "_png")
        os.makedirs(jpg_folder, exist_ok=True)
        os.makedirs(png_folder, exist_ok=True)

        try:
            t1=time.time()
            targetImage = Image.open(filepath)
            metadata = PngInfo()
            uuid4=uuid.uuid4()        
            metadata.add_text("ImageUniqueID",str(uuid4))

            targetImage.save(os.path.join(png_folder, newimgname + "_PIL.png"), pnginfo=metadata,compress_level=3)

            t2=time.time()
            print(f"PIL Time : {t2-t1}")

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
                uuid4=uuid.uuid4()   
                img.image_unique_id=str(uuid4)
                
            with open(os.path.join(jpg_folder, newimgname + ".jpg"), 'wb') as img_file2:
                img_file2.write(img.get_file())
            t2=time.time()   
            print(f"CV JPG Time : {t2-t1}") 

            t1=time.time()
            cv.imwrite(os.path.join(png_folder, newimgname + ".png"), imgg)
            t2=time.time()
            print(f"CV PNG Time : {t2-t1}") 
            ## yaml
            #metadataframe.write_meta(jpg_folder,newimgname + ".jpg")
            #metadataframe.write_meta(png_folder,newimgname + ".png")
        except:
            print("error saving")
            pass

    def start_segmenter(self):
        segmenter_settings = self.master.segmenter_frame.get_settings()  # type: ignore
        self.master.print(str(segmenter_settings))  # type: ignore
        Thread(
            target=MaxSegmenterModule.run_segmenter,
            args=(
                segmenter_settings["source_folder"],
                segmenter_settings["save_crops"],
                segmenter_settings["save_marked_imgs"],
                float(segmenter_settings["min_area_to_segment"]),
                float(segmenter_settings["min_area_to_save"]),
                segmenter_settings["save_path"],
                segmenter_settings["equalize_hist"],
                segmenter_settings["equalize_hist"],
                segmenter_settings["clear_save_path"],
                int(segmenter_settings["bg_size"]),
                int(segmenter_settings["max_threads"]),
                float(segmenter_settings["n_sigma"]),
                int(segmenter_settings["n_cores"]),
                segmenter_settings["mask_imgs"],
                int(segmenter_settings["mask_radius_offset"]),
                self.master,
            ),
        ).start()

    def start_pipeline(self):
        segmenter_settings = self.master.segmenter_frame.get_settings()  # type: ignore
        evaluation_settings = self.master.evaluation_frame.get_settings()  # type: ignore
        metadata_settings = self.master.metadata_frame.get_settings()  # type: ignore

        self.master.print(f"Segmenter settings: {str(segmenter_settings)}")  # type: ignore
        self.master.print(f"Evaluation settings: {str(evaluation_settings)}")  # type: ignore

        Thread(
            target=pipeline.main,
            args=(
                metadata_settings["source_folder"],#"home/pisco-controller/SO298-Segmentation/",
                segmenter_settings["save_crops"],
                segmenter_settings["save_marked_imgs"],
                float(segmenter_settings["min_area_to_segment"]),
                float(segmenter_settings["min_area_to_save"]),
                segmenter_settings["equalize_hist"],
                segmenter_settings["resize"],
                segmenter_settings["clear_save_path"],
                int(segmenter_settings["bg_size"]),
                int(segmenter_settings["max_threads"]),
                float(segmenter_settings["n_sigma"]),
                int(segmenter_settings["n_cores"]),
                segmenter_settings["mask_imgs"],
                int(segmenter_settings["mask_radius_offset"]),
                float(evaluation_settings["size_of_depth_bins"]),
                float(evaluation_settings["size_of_area_bins"]),
                evaluation_settings["only_saved"],
                self.master.metadata_frame,
                self.master,
            ),
        ).start()
    
    def start_single_pipe(self):
        segmenter_settings = self.master.segmenter_frame.get_settings()  # type: ignore
        evaluation_settings = self.master.evaluation_frame.get_settings()  # type: ignore
        metadata_settings = self.master.metadata_frame.get_settings()  # type: ignore

        self.master.print(f"Segmenter settings: {str(segmenter_settings)}")  # type: ignore
        self.master.print(f"Evaluation settings: {str(evaluation_settings)}")  # type: ignore

        Thread(
            target=single_pipe.main,
            args=(
                metadata_settings["source_folder"],#home/pisco-controller/SO298-Segmentation/",
                segmenter_settings["save_crops"],
                segmenter_settings["save_marked_imgs"],
                float(segmenter_settings["min_area_to_segment"]),
                float(segmenter_settings["min_area_to_save"]),
                segmenter_settings["equalize_hist"],
                segmenter_settings["resize"],
                segmenter_settings["clear_save_path"],
                int(segmenter_settings["bg_size"]),
                int(segmenter_settings["max_threads"]),
                float(segmenter_settings["n_sigma"]),
                int(segmenter_settings["n_cores"]),
                segmenter_settings["mask_imgs"],
                int(segmenter_settings["mask_radius_offset"]),
                float(evaluation_settings["size_of_depth_bins"]),
                float(evaluation_settings["size_of_area_bins"]),
                evaluation_settings["only_saved"],
                self.master.metadata_frame,
                self.master,
            ),
        ).start()
    
    def help(self):
        showinfo(title="Help", message="This is a help window")
