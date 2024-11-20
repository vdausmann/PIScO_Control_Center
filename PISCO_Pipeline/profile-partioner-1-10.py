import sys
import os
from os import path
import tkinter as tk
import customtkinter as ctk
from tkinter.filedialog import askdirectory
import shutil


def list_full_paths(directory):
        return [os.path.join(directory, file) for file in os.listdir(directory)]

### sort images by timestamp
def imsorttime(x):
        
        y=os.path.basename(x)
        try:
            ti=y[0:7]+x[9:14]

            return(int(ti))
            
        except ValueError:
            return(0)


dir = askdirectory()
im_files=list_full_paths(dir)
cnt=0
save_folder = dir + "_Segmentation_results/"
os.makedirs(save_folder, exist_ok=True)
for image in sorted(im_files, key = imsorttime):
    cnt=cnt+1
    if cnt==10:
        cnt=0
        shutil.copy(image,save_folder)

