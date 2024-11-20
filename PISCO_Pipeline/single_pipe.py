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
from tkinter.filedialog import askdirectory
import ruamel.yaml
import pickle
import pandas as pd

from PIL import Image ,ImageFile, ImageOps
ImageFile.LOAD_TRUNCATED_IMAGES = True
from PIL.PngImagePlugin import PngImageFile, PngInfo

from exif import Image as exIm

from datetime import datetime

import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))


## uncommented for testing !!!!!!!!!!!!!!!!!!!!

from MaxSegmenterProcessPool.segmenter import run_segmenter
from PISCO_Pipeline.processing_pipeline import gen_crop_df, plot_histogram, populate_esd_bins_pressure, plot_particle_dist, plot_2d_histogram, plot_position_hist, add_hist_value, plot_means
from PISCO_Pipeline.Imageselector import safe_sampleimgs
from PISCO_Pipeline.Logfile_hist import plot_log
# from PISCO_DataGenerator import generate_matrix

from PISCO_Pipeline.Classify_ViT import load_unclassified_images, transform, get_predictions_on_dataset_in_batches

#SAVE_FOLDER = "/Images/SO298/"
SAVE_FOLDER = "/home/pisco-controller/M202/"
LOG_FOLDER="/home/pisco-controller/SO308/Logfiles/"




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
    jpg_folder_txt = os.path.join(os.path.dirname(parent_folder), newdirname + "_jpg_txt")
    
    png_folder = os.path.join(os.path.dirname(parent_folder), newdirname + "_png")
    png_folder_txt = os.path.join(os.path.dirname(parent_folder), newdirname + "_png_txt")

    os.makedirs(jpg_folder, exist_ok=True)
    os.makedirs(png_folder, exist_ok=True)
    os.makedirs(jpg_folder_txt, exist_ok=True)
    os.makedirs(png_folder_txt, exist_ok=True)
 


    try:
        t1=time.time()
        targetImage = Image.open(filepath)
        metadata = PngInfo()
        uuid4_png=str(uuid.uuid4())        
        metadata.add_text("ImageUniqueID",uuid4_png)

        targetImage.save(os.path.join(png_folder, newimgname + ".png"), pnginfo=metadata,compress_level=3)
        sha256_hash_png = hashlib.sha256()
        with open(os.path.join(png_folder, newimgname + ".png"),"rb") as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096),b""):
                sha256_hash_png.update(byte_block)
            sha256_hash_png.hexdigest()
        with open(os.path.join(png_folder_txt, newimgname + ".txt"),'w') as f:
            f.write(uuid4_png + '\n')
            f.write(sha256_hash_png.hexdigest() +'\n')

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
        sha256_hash_jpg = hashlib.sha256()
        with open(os.path.join(jpg_folder, newimgname + ".jpg"),"rb") as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096),b""):
                sha256_hash_jpg.update(byte_block)
            sha256_hash_jpg.hexdigest() 
        with open(os.path.join(jpg_folder_txt, newimgname + ".txt"),'w') as f:
            f.write(uuid4_jpg + '\n')
            f.write(sha256_hash_jpg.hexdigest() +'\n')

        t2=time.time()   
        #print(f"CV JPG Time : {t2-t1}") 

        # t1=time.time()
        # cv.imwrite(os.path.join(png_folder, newimgname + ".png"), imgg)
        # t2=time.time()
        # print(f"CV PNG Time : {t2-t1}") 
        
        sha256_hash_jpg=0
        sha256_hash_png=0
        ## yaml
        # t1=time.time()
        # with yaml_Lock:
        #     metadataframe.write_meta(jpg_folder,newimgname + ".jpg",uuid4_jpg,date,press,sha256_hash_jpg)        
        #     metadataframe.write_meta(png_folder,newimgname + ".png",uuid4_png,date,press,sha256_hash_png)
        # t2=time.time()  
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
    yaml = ruamel.yaml.YAML()
    max_threads = 12
    filepath=files[0]
    parent_folder = os.path.dirname(filepath)
    fn = os.path.basename(filepath)
    [newdirname,newimgname,date,press]=metadataframe.get_filename(filepath)
   
    jpg_folder = os.path.join(os.path.dirname(parent_folder), newdirname + "_jpg")
    jpg_folder_txt = os.path.join(os.path.dirname(parent_folder), newdirname + "_jpg_txt")
    
    png_folder = os.path.join(os.path.dirname(parent_folder), newdirname + "_png")
    png_folder_txt = os.path.join(os.path.dirname(parent_folder), newdirname + "_png_txt")

    os.makedirs(jpg_folder, exist_ok=True)
    os.makedirs(png_folder, exist_ok=True)
    os.makedirs(jpg_folder_txt, exist_ok=True)
    os.makedirs(png_folder_txt, exist_ok=True)
    metadataframe.write_meta_csv(jpg_folder)
    metadataframe.write_meta_csv(png_folder)
    
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

    pressurefactor=0.990102748343775

    pngtexts=list_full_paths(png_folder_txt)      
    fn = os.path.basename(pngtexts[0])
    
    #create dicitonary
    yampa=os.path.join(png_folder,fn[:-4]+ ".png"  )
    yamlpath=os.path.dirname(yampa)+'/'+os.path.basename(os.path.dirname(yampa))+'.yaml'
    (camitem,yamlfile,meta)=metadataframe.init_yaml(png_folder, fn[:-4]+ ".png" ,yamlpath)
    init_yaml_file_tim(yamlpath,yamlfile)  
    
    info={}  
    for file in pngtexts: 
        t1=time.time()   
        fn = os.path.basename(file)
        time_ac=fn.split("_")[-1][:-4]
        dateti=time_ac
        newpress=float(fn.split("_")[-2][0:7])
        image=fn[:-4]+ ".png"
        with open(file,'r') as f:
            uuid =f.readline()
            hash=f.readline()
        dateyaml=dateti[0:4]+'-'+dateti[4:6]+'-'+dateti[6:8]+' '+dateti[9:11]+':'+dateti[11:13]+':'+dateti[13:15]+"."+dateti[15:17]

        info[image] = {
        "image-uuid": uuid[:-2],
        "image-hash": hash[:-2],
        "image-datetime": dateyaml,
        "image-longitude": "-123.854637",
        "image-latitude": "42.133426",
        "image-depth": float(newpress * pressurefactor),
        }    
        append_entry(yamlpath, info)
          
        #metadataframe.write_meta(png_folder,fn[:-4] + ".png",uuid,time_ac,newpress,hash)
        #yamfile=metadataframe.update_Yaml_Pipe(image,camitem,yamlfile,meta,dateyaml,newpress,uuid,hash)
        #with open(png_folder+'/'+os.path.basename(os.path.dirname(pngtexts[0]))+'.yaml','w') as newyamlfile:
        #     yaml.dump(yamfile, newyamlfile) 
        
        t2=time.time() 
        print(f"write_meta time png : {t2-t1}")   
    yamlfile['image-set-items']=info    
    with open(yamlpath[:-5]+'.pickle', "bw") as f:
        pickle.dump(yamlfile, f)

    
    
    jpgtexts=list_full_paths(jpg_folder_txt)      
    fn = os.path.basename(jpgtexts[0])
    
    #create dicitonary
    yampa=os.path.join(jpg_folder,fn[:-4]+ ".jpg"  )
    yamlpath=os.path.dirname(yampa)+'/'+os.path.basename(os.path.dirname(yampa))+'.yaml'
    (camitem,yamlfile,meta)=metadataframe.init_yaml(png_folder, fn[:-4]+ ".jpg" ,yamlpath)
    init_yaml_file_tim(yamlpath,yamlfile)  
    
    info={}  
    for file in jpgtexts: 
        t1=time.time()   
        fn = os.path.basename(file)
        time_ac=fn.split("_")[-1][:-4]
        dateti=time_ac
        newpress=float(fn.split("_")[-2][0:7])
        image=fn[:-4]+ ".jpg"
        with open(file,'r') as f:
            uuid =f.readline()
            hash=f.readline()
        dateyaml=dateti[0:4]+'-'+dateti[4:6]+'-'+dateti[6:8]+' '+dateti[9:11]+':'+dateti[11:13]+':'+dateti[13:15]+"."+dateti[15:17]

        info[image] = {
        "image-uuid": uuid[:-2],
        "image-hash": hash[:-2],
        "image-datetime": dateyaml,
        "image-longitude": "-123.854637",
        "image-latitude": "42.133426",
        "image-depth": float(newpress * pressurefactor),
        }    
        append_entry(yamlpath, info)
          
        #metadataframe.write_meta(png_folder,fn[:-4] + ".png",uuid,time_ac,newpress,hash)
        #yamfile=metadataframe.update_Yaml_Pipe(image,camitem,yamlfile,meta,dateyaml,newpress,uuid,hash)
        #with open(png_folder+'/'+os.path.basename(os.path.dirname(pngtexts[0]))+'.yaml','w') as newyamlfile:
        #     yaml.dump(yamfile, newyamlfile) 
        
        t2=time.time() 
        print(f"write_meta time jpg : {t2-t1}")   
    yamlfile['image-set-items']=info    
    with open(yamlpath[:-5]+'.pickle', "bw") as f:
        pickle.dump(yamlfile, f)





    # fn = os.path.basename(jpgtexts[0])
    # (camitem,yamlfile,meta)=metadataframe.init_yaml(jpg_folder, fn[:-4]+ ".png" )
    # for file in jpgtexts:   
    #     fn = os.path.basename(file)
    #     time_ac=fn.split("_")[-1][:-4]
    #     dateti=time_ac
    #     newpress=float(fn.split("_")[-2][0:7])
    #     image=fn[:-4]+ ".png"
    #     with open(file,'r') as f:
    #         uuid =f.readline()
    #         hash=f.readline()
    #     dateyaml=dateti[0:4]+'-'+dateti[4:6]+'-'+dateti[6:8]+' '+dateti[9:11]+':'+dateti[11:13]+':'+dateti[13:15]+"."+dateti[15:17]

    #     info[image] = {
    #     "image-uuid": uuid[:-2],
    #     "image-hash": hash[:-2],
    #     "image-datetime": dateyaml,
    #     "image-longitude": "-123.854637",
    #     "image-latitude": "42.133426",
    #     "image-depth": float(newpress * pressurefactor),
    #     }    
        
    #     t1=time.time()   
    #     #metadataframe.write_meta(png_folder,fn[:-4] + ".png",uuid,time_ac,newpress,hash)
    #     yamfile=metadataframe.update_Yaml_Pipe(image,camitem,yamlfile,meta,dateyaml,newpress,uuid,hash)
    #     with open(jpg_folder+'/'+os.path.basename(os.path.dirname(jpgtexts[0]))+'.yaml','w') as newyamlfile:
    #                                             yaml.dump(yamfile, newyamlfile) 
        
    #     t2=time.time() 
    #     print(f"write_meta time jpg : {t2-t1}")   


    # for file in jpgtexts:   
    #     fn = os.path.basename(file)
    #     time_ac=fn.split("_")[-1][:-4]
    #     dateti=time_ac
    #     newpress=float(fn.split("_")[-2][0:7])
    #     image=fn[:-4]+ ".jpg"
    #     with open(file,'r') as f:
    #         uuid =f.readline()
    #         hash=f.readline()
    #     dateyaml=dateti[0:4]+'-'+dateti[4:6]+'-'+dateti[6:8]+' '+dateti[9:11]+':'+dateti[11:13]+':'+dateti[13:15]+"."+dateti[15:17]
    #     t1=time.time()   
    #     #metadataframe.write_meta(png_folder,fn[:-4] + ".png",uuid,time_ac,newpress,hash)
    #     yamfile=metadataframe.update_Yaml_Pipe(image,camitem,yamlfile,meta,dateyaml,newpress,uuid,hash)
    #     with open(jpg_folder+'/'+os.path.basename(os.path.dirname(jpgtexts[0]))+'.yaml','w') as newyamlfile:
    #                                             yaml.dump(yamfile, newyamlfile) 
        
    #     t2=time.time() 
    #     print(f"write_meta time jpg : {t2-t1}")  

    # pngtexts=list_full_paths(png_folder_txt)      
        
    # for file in pngtexts:   
    #      fn = os.path.basename(file)
    #      time_ac=fn.split("_")[-1][:-4]
    #      newpress=float(fn.split("_")[-2][0:7])
    #      with open(file,'r') as f:
    #         uuid =f.readline()
    #         hash=f.readline()
    #      metadataframe.write_meta(png_folder,fn[:-4] + ".png",uuid,time_ac,newpress,hash)    

    # jpgtexts=list_full_paths(jpg_folder_txt)      
        
    # for file in jpgtexts:   
    #      fn = os.path.basename(file)
    #      time_ac=fn.split("_")[-1][:-4]
    #      newpress=float(fn.split("_")[-2][0:7])
    #      with open(file,'r') as f:
    #         uuid =f.readline()
    #         hash=f.readline()
    #      metadataframe.write_meta(jpg_folder,fn[:-4] + ".jpg",uuid,time_ac,newpress,hash)         
    return(png_folder)            


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

def delete_camera_folders():
    proc = subprocess.Popen(
        "exec sshpass -p "
        "pw19"
        " ssh plankdeep@192.168.0.1 'find '/images' -mindepth 1 -delete'",
        
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


def get_files(csv_file: str, save_folder: str):
    with open(csv_file, "r") as f:
        data = list(csv.reader(f, delimiter=","))

    #check for more then one profiles
    multiprofile=False
    if data:
        if (data[0][0].split('/')[0]!=  data[len(data)-1][0].split('/')[0]  or data[0][0].split('/')[1]!=  data[len(data)-1][0].split('/')[1]):
            multiprofile=True
            
    data = [os.path.join(save_folder, fn[0]) for fn in data]
    return (data,multiprofile)


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

def list_full_paths(directory):
        return [os.path.join(directory, file) for file in os.listdir(directory)]

def get_field(s: str):
    field_substr = s.split(" ")
    field = field_substr[-1]
    index = s.find(field)
    return index

def init_yaml_file_tim(path, info: dict):
    with open(path, "w") as f:
        f.write("image-set-header:\n")
        info = info["image-set-header"]
        for key in info.keys():
            f.write(" " * 4 + f"{key}: ")
            if type(info[key]) == dict:
                f.write("\n")
                key2 = list(info[key].keys())[0]
                offset = get_field(key2)
                f.write(" " * 8 + f"{key2}: {info[key][key2]}\n")
                for key2 in list(info[key].keys())[1:]:
                    f.write(" " * 8 + " " * offset + f"{key2}: {info[key][key2]}\n")
            if type(info[key]) == list:
                 f.write("\n")
                 dictlist=list(info[key])
                 for dicts in dictlist:
                    key2 = list(dicts.keys())
                    f.write(" " * 8 + "- " + key2[0]+": "+ dicts[key2[0]]+"\n")
                    for x in range(1,len(key2)):
                         f.write(" " * 10 + key2[x]+": "+ dicts[key2[x]]+"\n")

                 


            else:
            
                if type(info[key])==str:
                    f.write(info[key]+"\n")
                else:
                    f.write("\n")  

               
                # for i, row in enumerate(info[key]):
                #     if i > 0:
                #         f.write(" " * 8 + f"{row}\n")
                #     else:
                #         f.write(f"{row}\n")                        
        f.write("image-set-items:\n")


def append_entry(path, info: dict):
    with open(path, "a") as f:
        key = list(info.keys())[-1]
        # for key in info.keys():
        f.write(" " * 4 + f"{key}:\n")
        for key2 in info[key].keys():
            f.write(" " * 8 + f"{key2}: {info[key][key2]}\n")


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
    print_message(app, "Single pipeline started...")
    
    # convert imgs
    # erstelle yaml
    print_message(app, "Converting images...")
    print_message(app, "Select Raw Image Folder")

    dir = askdirectory()
    #metadataframe.source_folder.set(dir)
    #print(metadataframe.settings["source_folder"].get())
    
    im_files=list_full_paths(dir)
    #im_files=os.listdir(dir)    
    profile=convert_imgs(im_files, metadataframe)
    print_message(app, "All images converted")

   
    print_message(app, f"Start segmenting {profile}")
    save_folder = profile + "_Segmentation_results/"
    os.makedirs(save_folder, exist_ok=True)

    run_segmenter(profile,save_folder,True) #set DECONVOLUTION here
    #plot_path = profile+'/'+os.path.basename(profile) 
    df = gen_crop_df(os.path.join(save_folder,'Data'), small=True)
    press_min = df['pressure [dbar]'].min()-10
    plot_histogram(df, save_folder)
    depth_bin_size = 5
    _, pivoted = populate_esd_bins_pressure(df, depth_bin_size=depth_bin_size)
    plot_particle_dist(pivoted, os.path.basename(profile), save_folder, depth_bin_size=depth_bin_size, preliminary=True, depth_min=press_min)
    plot_position_hist(df,save_folder)
    plot_2d_histogram(df,save_folder)
    add_hist_value(df)
    plot_means(df,save_folder)

    df.to_csv(os.path.join(save_folder,'meta_dataframe.csv'),index=True)
    safe_sampleimgs(profile,os.path.join(save_folder,'meta_dataframe.csv'))
    plot_log(profile,save_folder,LOG_FOLDER)

    print_message(app, f"Finished segmenting {profile}, starting classification...")

    #### C L A S S I F I C A T I O N ####

    # Load the dataset and include filenames
    root_dir = save_folder
    img_dir = os.path.join(root_dir, 'Crops')
    
    ds_pisco = load_unclassified_images(img_dir)

    # Apply the transform to the dataset
    ds_pisco_trans = ds_pisco.with_transform(transform)
    print(ds_pisco_trans)

    # Define model name and path to the saved model
    model_dir = '/home/pisco-controller/Desktop/Classifier/best_model'

    # Get predictions on the dataset in batches
    filenames, predictions, probabilities = get_predictions_on_dataset_in_batches(ds_pisco_trans, model_dir, batch_size=128)

    # Create a DataFrame and store it on disk
    df = pd.DataFrame({
        'filename': filenames,
        'top1': [pred[0] for pred in predictions],
        'top2': [pred[1] for pred in predictions],
        'top3': [pred[2] for pred in predictions],
        'top4': [pred[3] for pred in predictions],
        'top5': [pred[4] for pred in predictions],
        'prob1': [prob[0] for prob in probabilities],
        'prob2': [prob[1] for prob in probabilities],
        'prob3': [prob[2] for prob in probabilities],
        'prob4': [prob[3] for prob in probabilities],
        'prob5': [prob[4] for prob in probabilities]
    })    
    result_path = os.path.join(root_dir,'ViT_predictions.csv')
    df.to_csv(result_path, index=False)
    print("Predictions saved!")

    # Print the first 5 predictions
    print('Classification done. Have fun validating! ;)')
    print(df.head())


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
