import tkinter as tk
import customtkinter as ctk
from tkinter.filedialog import askdirectory
import pickle
import os,sys
import time
import csv
import random
import math
import matplotlib.pyplot as plt
import numpy as np
import datetime
import yaml
import pandas as pd
import os.path
import time
import tkinter
from tkinter.filedialog import askdirectory
from PIL import Image ,ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
from PIL.PngImagePlugin import PngImageFile, PngInfo
import yaml
import ruamel.yaml
from copy import deepcopy
import hashlib
import uuid
from exif import Image as exIm
import threading
from scipy import spatial
from tkinter.filedialog import askopenfilename
from pathlib import Path

yaml_Lock=threading.Lock()

class MetadataFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        # setting variables
        self.source_folder = tk.StringVar(self, "") 
        self.target_folder = tk.StringVar(self, "") 
        self.ctd_file = tk.StringVar(self, "") 
        self.templog_file = tk.StringVar(self, "")
        self.Datetimeprofile = tk.StringVar(self, "0")      
        self.Latitude = tk.StringVar(self, "0")
        self.Longitude = tk.StringVar(self, "0")
        self.DShipID = tk.StringVar(self, "0")
        self.CTDprofileid = tk.StringVar(self, "0")
        self.Depthtotal = tk.StringVar(self, "0")
        self.Depthprofile = tk.StringVar(self, "0")
        self.Cameraframerate = tk.StringVar(self, "0")
        self.Cameraresolution = tk.StringVar(self, "0")
        self.Pixelpermm = tk.StringVar(self, "0")
        self.Flashduration = tk.StringVar(self, "0")
        self.Flashpower = tk.StringVar(self, "0")
        self.Tagamplitude = tk.StringVar(self, "0")
        self.Camera = tk.StringVar(self, "0")
        self.Cruise = tk.StringVar(self, "0")
        self.Platform = tk.StringVar(self, "0")
        self.Comment = tk.StringVar(self, "0")
        self.Binning = tk.StringVar(self, "0")
        self.Gain = tk.StringVar(self, "0")
        self.lenssystem = tk.StringVar(self, "")
        self.mirror_adjusted = tk.BooleanVar(self, False)
        

        self.settings = {
            "source_folder": self.source_folder,
            "target_folder":self.target_folder,
            "ctd_file": self.ctd_file,
            "templog_file": self.templog_file,
            "Datetimeprofile": self.Datetimeprofile,
            "Latitude": self.Latitude,
            "Longitude": self.Longitude,
            "DShipID": self.DShipID,
            "CTDprofileid": self.CTDprofileid,
            "Depthtotal": self.Depthtotal,
            "Depthprofile": self.Depthprofile,
            "Cameraframerate": self.Cameraframerate,
            "Cameraresolution": self.Cameraresolution,
            "Pixelpermm": self.Pixelpermm,
            "Flashduration": self.Flashduration,
            "Flashpower": self.Flashpower,
            "Tagamplitude": self.Tagamplitude,
            "Camera": self.Camera,
            "Cruise": self.Cruise,
            "Platform": self.Platform,
            "Comment": self.Comment,
            "Gain": self.Gain,
            "Binning": self.Binning,
            "mirror_adjusted":self.mirror_adjusted,
            "Lenssystem":self.lenssystem
            
        }

        # source folder
        ctk.CTkLabel(self, text="Set Save Directory:").grid(row=0, column=0)
        ctk.CTkButton(
            self,
            text="Choose folder",
            width=100,
            command=lambda: self.choose_folder(self.source_folder),
        ).grid(row=1, column=0, pady=5, padx=5)
        print(self.settings["source_folder"].get())
        ctk.CTkLabel(self, text="Source folder:").grid(row=4, column=5)
        ctk.CTkLabel(self, text=self.settings["source_folder"].get()).grid(row=5, column=5)
        
        # ctd_file
        ctk.CTkLabel(self, text="ctd_file:").grid(row=4, column=7)
        ctk.CTkButton(
            self,
            text="Choose Ctd file",
            width=100,
            command=lambda: self.choose_ctdfile(self.ctd_file),
        ).grid(row=5, column=7, pady=5, padx=5)

        # ctd_file
        ctk.CTkLabel(self, text="templog_file:").grid(row=4, column=8)
        ctk.CTkButton(
            self,
            text="Choose Templog file",
            width=100,
            command=lambda: self.choose_ctdfile(self.templog_file),
        ).grid(row=5, column=8, pady=5, padx=5)

       
        # Start Renaming
        ctk.CTkLabel(self, text="Start Renaming with Metadata:").grid(row=4, column=6)
        ctk.CTkButton(
            self,
            text="Start",
            width=100,
            command=self.rename_imgs
        ).grid(row=5, column=6, pady=5, padx=5)

        # GPS Latitude
        ctk.CTkLabel(self, text="Latitude (example: 10° 23,2563' S)").grid(
            row=0, column=1, pady=5, padx=5
        )
        ctk.CTkEntry(self, width=200, textvariable=self.Latitude).grid(
            row=1, column=1, pady=5, padx=5
        )

        # GPS Longitude
        ctk.CTkLabel(self, text="Longitude (example: 010° 23,2563' W)").grid(
            row=0, column=2, pady=5, padx=5
        )
        ctk.CTkEntry(self, width=200, textvariable=self.Longitude).grid(
            row=1, column=2, pady=5, padx=5
        )

        # DShipID
        ctk.CTkLabel(self, text="DShip-ID").grid(
            row=0, column=3, pady=5, padx=5
        )
        ctk.CTkEntry(self, width=150, textvariable=self.DShipID).grid(
            row=1, column=3, pady=5, padx=5
        )

         # CTDprofileid
        ctk.CTkLabel(self, text="CTD-Profile-ID").grid(
            row=0, column=4, pady=5, padx=5
        )
        ctk.CTkEntry(self, width=200, textvariable=self.CTDprofileid).grid(
            row=1, column=4, pady=5, padx=5
        )



        # Depthtotal
        ctk.CTkLabel(self, text="Bottom-Depth").grid(
            row=0, column=5, pady=5, padx=5
        )
        ctk.CTkEntry(self, width=80, textvariable=self.Depthtotal).grid(
            row=1, column=5, pady=5, padx=5
        )

        # Depthprofile
        ctk.CTkLabel(self, text="Profile Depth").grid(
            row=0, column=6, pady=5, padx=5
        )
        ctk.CTkEntry(self, width=80, textvariable=self.Depthprofile).grid(
            row=1, column=6, pady=5, padx=5
        )

        # Datetimeprofile
        ctk.CTkLabel(self, text="Date Time UTC: YYYYMMDD HHMM").grid(
            row=0, column=7, pady=5, padx=5
        )
        ctk.CTkEntry(self, width=200, textvariable=self.Datetimeprofile).grid(
            row=1, column=7, pady=5, padx=5
        )

        # Cameraframerate
        ctk.CTkLabel(self, text="Cameraframerate (fps)").grid(
            row=2, column=0, pady=5, padx=5
        )
        ctk.CTkEntry(self, width=60, textvariable=self.Cameraframerate).grid(
            row=3, column=0, pady=5, padx=5
        )

        # Cameraresolution
        ctk.CTkLabel(self, text="Cameraresolution (xpixel x ypixel)").grid(
            row=2, column=1, pady=5, padx=5
        )
        ctk.CTkEntry(self, width=150, textvariable=self.Cameraresolution).grid(
            row=3, column=1, pady=5, padx=5
        )

        # Pixelpermm
        ctk.CTkLabel(self, text="um per pixel").grid(
            row=2, column=2, pady=5, padx=5
        )
        ctk.CTkEntry(self, width=80, textvariable=self.Pixelpermm).grid(
            row=3, column=2, pady=5, padx=5
        )

        # Flashduration
        ctk.CTkLabel(self, text="Flashduration (us)").grid(
            row=2, column=3, pady=5, padx=5
        )
        ctk.CTkEntry(self, width=60, textvariable=self.Flashduration).grid(
            row=3, column=3, pady=5, padx=5
        )

        # Flashpower
        ctk.CTkLabel(self, text="Flashpower").grid(
            row=2, column=4, pady=5, padx=5
        )
        ctk.CTkEntry(self, width=60, textvariable=self.Flashpower).grid(
            row=3, column=4, pady=5, padx=5
        )

        # Tagamplitude
        ctk.CTkLabel(self, text="Tagamplitude (%)").grid(
            row=2, column=4, pady=5, padx=5
        )
        ctk.CTkEntry(self, width=60, textvariable=self.Tagamplitude).grid(
            row=3, column=4, pady=5, padx=5
        )

        # Cruise
        ctk.CTkLabel(self, text="Cruise").grid(
            row=2, column=5, pady=5, padx=5
        )
        ctk.CTkEntry(self, width=100, textvariable=self.Cruise).grid(
            row=3, column=5, pady=5, padx=5
        )

        # Camera
        ctk.CTkLabel(self, text="Camera").grid(
            row=2, column=6, pady=5, padx=5
        )
        ctk.CTkEntry(self, width=150, textvariable=self.Camera).grid(
            row=3, column=6, pady=5, padx=5
        )

        # Platform
        ctk.CTkLabel(self, text="Platform").grid(
            row=2, column=7, pady=5, padx=5
        )
        ctk.CTkEntry(self, width=100, textvariable=self.Platform).grid(
            row=3, column=7, pady=5, padx=5
        )
        # Comment
        ctk.CTkLabel(self, text="Comment").grid(
            row=4, column=0, pady=5, padx=5
        )
        ctk.CTkEntry(self, width=300, textvariable=self.Comment).grid(
            row=5, column=0, pady=5, padx=5
        )

        # Binning
        ctk.CTkLabel(self, text="Binning").grid(
            row=4, column=1, pady=5, padx=5
        )
        ctk.CTkEntry(self, width=80, textvariable=self.Binning).grid(
            row=5, column=1, pady=5, padx=5
        )

        # Gain
        ctk.CTkLabel(self, text="Gain").grid(
            row=4, column=2, pady=5, padx=5
        )
        ctk.CTkEntry(self, width=80, textvariable=self.Gain).grid(
            row=5, column=2, pady=5, padx=5
        )

        # Flashpower
        ctk.CTkLabel(self, text="Flashpower").grid(
            row=4, column=3, pady=5, padx=5
        )
        ctk.CTkEntry(self, width=80, textvariable=self.Flashpower).grid(
            row=5, column=3, pady=5, padx=5
        )

        # Lenssystem
        ctk.CTkLabel(self, text="Lenssystem: F Light - F Cam1 - F Cam2 ").grid(
            row=6, column=1, pady=5, padx=5
        )
        ctk.CTkEntry(self, width=300, textvariable=self.lenssystem).grid(
            row=7, column=1, pady=5, padx=5
        )

        # "Mirrow adjusted:"
        ctk.CTkLabel(self, text="Mirrow adjusted:").grid(
            row=4, column=4, pady=5, padx=5
        )
        ctk.CTkCheckBox(self, text="", variable=self.mirror_adjusted).grid(
            row=5, column=4, pady=5, padx=5
        )

    def get_settings(self):
        return {key: self.settings[key].get() for key in self.settings.keys()}

    def set_settings(self, settings: dict):
        for key in settings:
            self.settings[key].set(settings[key])

    def choose_folder(self, var):
        dir = askdirectory()
        var.set(dir)
        print(self.settings["source_folder"].get())
        
        ctk.CTkLabel(self, text=self.settings["source_folder"].get()).grid(row=5, column=5)

    def choose_ctdfile(self, var):
        dir = askopenfilename()
        var.set(dir)
        print(self.settings["ctd_file"].get())
        
        ctk.CTkLabel(self, text=self.settings["ctd_file"].get()).grid(row=6, column=7)    
    
        

    def rename_imgs(self):

        if self.settings["ctd_file"].get()==[]:
             print ("choose the the fitting ctd_file")
             return()
        else:
             depthdata=self.get_depthdata(self.settings["ctd_file"].get())
        
        
        yaml = ruamel.yaml.YAML()
        folder=self.settings["source_folder"].get()
        tarfolder=self.target_folder
        pressurefactor=0.990102748343775
        
        #print(str(self.settings["Latitude"].get()))
        #print(len(str(self.settings["Latitude"].get())))
        #print(len(self.settings["Latitude"].get()))
        # "
        meta={}
        meta['profileid']= "p_"+str(self.settings["CTDprofileid"].get()) 
        meta['latitude_dec']= str(self.gps_deg_2_dec(self.settings["Latitude"].get()))
        meta['longitude_dec']= str(self.gps_deg_2_dec(self.settings["Longitude"].get()))
        meta['latitude_im']= str(self.gps_deg_2_imformat(self.settings["Latitude"].get()))
        meta['longitude_im']= str(self.gps_deg_2_imformat(self.settings["Longitude"].get()))
        meta['bottomdepth']= str(self.settings["Depthtotal"].get())
        meta['dship_id']= str(self.settings["DShipID"].get())
        camera=str(self.settings["Camera"].get())
        cruise=str(self.settings["Cruise"].get())

        datefolder=self.list_full_paths(folder)
        ImSaverrorls=[]
        max_threads = 13 
        timecorrection=False

        for dfol in datefolder:
            safe_fol=False
            #print(os.path.basename(dfol))
            #print(self.settings["Datetimeprofile"].get()[0:8])
            Timefolders= self.list_full_paths(dfol)
            [imfolli,cordate]=self.findmatching_timeprofile(Timefolders,timecorrection)
            if cordate[0:8]==self.settings["Datetimeprofile"].get()[0:8] :
            #if os.path.basename(dfol).startswith("2021"):
                safe_fol=True
                print(os.path.basename(dfol))
                #Timefolders= self.list_full_paths(dfol)
                #imfolli=self.findmatching_timeprofile(Timefolders,timecorrection)
                
                
                imfol=  self.list_full_paths(imfolli)
                for imgfol in imfol:
                    imfiles=os.listdir(imgfol)
                    #meta=findmatchingmeta(os.path.basename(imfol),metagps)
                    
                    print ('Start renaming of: ' +os.path.basename(imgfol) )
                    pressin=0
                    imwritten=False  
                   
                    [camitem,yamlfile]=self.get_Camkey(meta,camera,cruise)    
                        
                    yamwrite=False
                    startsort=True
                    png="png"
                    jpg="jpg"
                    filetypes=[png,jpg]
                    Step=0
                    
                    for fit in filetypes:
                        uuidlist=[]
                        Step=Step+1
                        imcnt=0
                        for image in sorted(imfiles, key = self.imsorttime):
                            
                            if os.path.basename(image)[0:4]=="2023":
                                if image.endswith('.png'):
                                        ft="png"
                                        uuid4=str(uuid.uuid4())
                                        
                                if image.endswith('.jpg'):
                                        ft="jpg"
                                        uuid4=str(uuid.uuid4())
                                        
                                print("for ft "+ ft + " threads: " + str(len(threading.enumerate()))+ " maxthread: " + str(max_threads))          
                                imcnt=imcnt+1
                                print (" Step : " +str(Step) + "Image: " +str(imcnt) + " of " + str(len(imfiles)))
                                uuidlist.append(uuid4)
                                while len(threading.enumerate())>max_threads:
                                    time.sleep(0.1)
                                    
                                    
                                   
                                print("threadstart") 
                                imagepathexif=imgfol+"/"+image  
                                print(imagepathexif)  
                                threading.Thread(target=self.write_exif, args=(ft,imagepathexif,uuid4,)).start()   
                                   
                        uuidkey=0
                        #time.sleep(3)  
                        #time.sleep(5)
                        Step=Step+1
                        imcnt=0
                        for image in sorted(imfiles, key = self.imsorttime):
                          if os.path.basename(image)[0:4]=="2023":  
                            if image.endswith('.tif') or image.endswith('.png') or image.endswith('.jpg'):
                                
                                imcnt=imcnt+1
                                print (" Step : " +str(Step) + "Image: " +str(imcnt) + " of " + str(len(imfiles)))
                               
                                
                                if image.endswith('.png'):
                                     ft="png"
                                if image.endswith('.jpg'):
                                     ft="jpg"     
                                im = os.path.basename(image)[:-4]
                                pressurefactor=self.get_pressurefactor(float(image[18:25]),depthdata)
                                
                                newpress=float(image[18:25])*10
                                
                                newimfolderpth=imgfol

                                #2019-05-13 13:14:15.0000
                                if timecorrection:
                                    type_cor=0
                                    oldtime=im[0:17]
                                    dateti=self.correct_time(oldtime,type_cor)[0]
                                else:
                                    dateti=  im[0:17]   

                                #dateti=im[0:17]
                                dateyaml=dateti[0:4]+'-'+dateti[4:6]+'-'+dateti[6:8]+' '+dateti[9:11]+':'+dateti[11:13]+':'+dateti[13:15]+"."+dateti[15:17]
                                
                                #dateti=im[0:17]
                                
                                newimagename=cruise+"_"+meta['dship_id']+"_"+camera+"_{:07.2f}dbar-".format(newpress)+meta['latitude_im']+"-"+meta['longitude_im']+"-"+image[-10:-4]+"_"+dateti
                                [newimfolderpthname,newimpath,imwritten]=self.writeimage(imgfol,image,newimagename,imfolli,dfol,meta,ft,dateti,camera,cruise)

                                if not imwritten:
                                                ImSaverrorls.append(newimpath)
                                        #else:
                                        #    pressin=pressin+1
                                        #check and wait that image is saved
                                if imwritten:
                                            imwritten=False
                                            timer=0
                                            while not os.path.exists(newimpath):
                                                time.sleep(0.1)
                                                timer=timer+1
                                                if timer>50:
                                                    print('no image saved in 5 seconds Skipping Image !')
                                                    break
                                            if os.path.isfile(newimpath):
                                               yamfile=self.update_Yaml(newimpath,camitem,yamlfile,meta,dateyaml,newpress,uuidlist[uuidkey]) 
                                               yamwrite=True 
                                               

                                            # if ft=="png": 
                                            #     if os.path.isfile(newimpath):
                                                                                                       
                                            #         # with open(newimpath, 'rb') as img_file:
                                            #         #     img2 = exIm(img_file)

                                            #         #     if img2.get("image_unique_id")==uuidlist[uuidkey]:
                                            #         #     #update yaml file
                                            #         #         yamfile=self.update_Yaml(newimpath,camitem,yamlfile,meta,dateyaml,newpress,uuidlist[uuidkey])
                                            #         #         yamwrite=True
                                            #         #     else:
                                            #         #         print('UUID JPG Metadatawrite Error!')
                                            #         #         print('Could not rename following images: \n') 
                                            #         # uuidkey=uuidkey+1   
                                            #         targetImage = PngImageFile(newimpath)
                                                    
                                            #         if targetImage.text['ImageUniqueID']== uuidlist[uuidkey]:
                                            #         #update yaml file
                                            #             yamfile=self.update_Yaml(newimpath,camitem,yamlfile,meta,dateyaml,newpress,uuidlist[uuidkey])
                                            #             yamwrite=True
                                            #         else:
                                            #             print('UUID PNG Metadatawrite Error!')
                                            #         uuidkey=uuidkey+1

                                            # if ft == "jpg":
                                            #     if os.path.isfile(newimpath):
                                                                                                       
                                            #         with open(newimpath, 'rb') as img_file:
                                            #             img2 = exIm(img_file)

                                            #             if img2.get("image_unique_id")==uuidlist[uuidkey]:
                                            #             #update yaml file
                                            #                 yamfile=self.update_Yaml(newimpath,camitem,yamlfile,meta,dateyaml,newpress,uuidlist[uuidkey])
                                            #                 yamwrite=True
                                            #             else:
                                            #                 print('UUID JPG Metadatawrite Error!')
                                            #                 print('Could not rename following images: \n') 
                            uuidkey=uuidkey+1                 #         uuidkey=uuidkey+1        
                        if yamwrite:
    
                            with open(imgfol+'/'+os.path.basename(newimfolderpthname)+'.yaml','w') as newyamlfile:
                                                    yaml.dump(yamfile, newyamlfile)     
                            yamwrite=False
                        for imerror in ImSaverrorls:
                            
                            print(imerror+'\n')

                    os.rename(imgfol,newimfolderpthname)
            
            if safe_fol:
                os.rename(imfolli,dfol + "/" + os.path.basename(newimfolderpthname)[:-4]) 
        
                print("Sucessfully renamed")       
                #settingssave=self.settings.get()
                root_dir = Path(__file__).resolve().parent.parent
                settingsfilnm=root_dir / "app_default_settings.pickle"
                with open(settingsfilnm, "rb") as f:
                    settingsdict = pickle.load(f)
                
                df=pd.DataFrame.from_dict(settingsdict[2],orient='index')
                df.to_csv(dfol + "/" + os.path.basename(newimfolderpthname)[:-4]+ "/" + os.path.basename(newimfolderpthname)[:-4] + "metadata_settings.csv")

    def write_meta_csv(self,folder):
                root_dir = Path(__file__).resolve().parent.parent
                settingsfilnm=root_dir / "app_default_settings.pickle"
                with open(settingsfilnm, "rb") as f:
                    settingsdict = pickle.load(f)
                
                df=pd.DataFrame.from_dict(settingsdict[2],orient='index')
                df.to_csv(folder + "/"  + os.path.basename(folder)[:-4] + "metadata_settings.csv") 
        
    def get_filename(self, image: str):
        print("image_name_full "+image)
        im=os.path.basename(image)[:-4]
        print("image_name "+im)
        newpress=float(im[18:25])*10
        dateti=  im[0:17]
        timeti=os.path.basename(os.path.dirname(image))

        meta={}
        meta['profileid']= "p_"+str(self.settings["CTDprofileid"].get()) 
        meta['latitude_dec']= str(self.gps_deg_2_dec(self.settings["Latitude"].get()))
        meta['longitude_dec']= str(self.gps_deg_2_dec(self.settings["Longitude"].get()))
        meta['latitude_im']= str(self.gps_deg_2_imformat(self.settings["Latitude"].get()))
        meta['longitude_im']= str(self.gps_deg_2_imformat(self.settings["Longitude"].get()))
        meta['bottomdepth']= str(self.settings["Depthtotal"].get())
        meta['dship_id']= str(self.settings["DShipID"].get())
        camera=str(self.settings["Camera"].get())
        cruise=str(self.settings["Cruise"].get())
        

        if os.path.basename(image)[0:4]==self.settings["Datetimeprofile"].get()[0:4]:
           
                                
            #dateti=im[0:17]
            newimpathname=timeti[0:8]+"-"+timeti[9:13]+"_"+meta['dship_id']+"_"+camera
            newimagename=meta['dship_id']+"_"+camera+"_{:07.2f}dbar-".format(newpress)+meta['latitude_im']+"-"+meta['longitude_im']+"-"+image[-10:-4]+"_"+dateti
        return  (newimpathname,newimagename,dateti,newpress)  

 
    ## write yaml
    def write_meta(self,folder:str, image:str,uuid4:str,dateti,newpress,hash):
        yaml = ruamel.yaml.YAML()
        image=os.path.join(folder, image ) 
        meta={}
        meta['profileid']= "p_"+str(self.settings["CTDprofileid"].get()) 
        meta['latitude_dec']= str(self.gps_deg_2_dec(self.settings["Latitude"].get()))
        meta['longitude_dec']= str(self.gps_deg_2_dec(self.settings["Longitude"].get()))
        meta['latitude_im']= str(self.gps_deg_2_imformat(self.settings["Latitude"].get()))
        meta['longitude_im']= str(self.gps_deg_2_imformat(self.settings["Longitude"].get()))
        meta['bottomdepth']= str(self.settings["Depthtotal"].get())
        meta['dship_id']= str(self.settings["DShipID"].get())
        camera=str(self.settings["Camera"].get())
        cruise=str(self.settings["Cruise"].get())
        yamlpath=os.path.dirname(image)+'/'+os.path.basename(os.path.dirname(image))+'.yaml'
        [camitem,yamlfile]=self.get_Camkey(meta,camera,cruise,yamlpath)

       
        dateyaml=dateti[0:4]+'-'+dateti[4:6]+'-'+dateti[6:8]+' '+dateti[9:11]+':'+dateti[11:13]+':'+dateti[13:15]+"."+dateti[15:17]

        yamfile=self.update_Yaml_Pipe(image,camitem,yamlfile,meta,dateyaml,newpress,uuid4,hash)
        #yamfile=self.update_Yaml(image,camitem,yamlfile,meta,dateyaml,newpress,uuid4)
        #print(os.path.dirname(image)+'/'+os.path.basename(os.path.dirname(image))+'.yaml','w')
        
        # with yaml_Lock:
        #     with open(os.path.dirname(image)+'/'+os.path.basename(os.path.dirname(image))+'.yaml','w') as newyamlfile:
        #                 yaml.dump(yamfile, newyamlfile) 
        
        with open(os.path.dirname(image)+'/'+os.path.basename(os.path.dirname(image))+'.yaml','w') as newyamlfile:
                        yaml.dump(yamfile, newyamlfile)                 
                                    
         
    def init_yaml(self,folder:str, image:str, yamlpath:str):
        yaml = ruamel.yaml.YAML()
        image=os.path.join(folder, image ) 
        meta={}
        meta['profileid']= "p_"+str(self.settings["CTDprofileid"].get()) 
        meta['latitude_dec']= str(self.gps_deg_2_dec(self.settings["Latitude"].get()))
        meta['longitude_dec']= str(self.gps_deg_2_dec(self.settings["Longitude"].get()))
        meta['latitude_im']= str(self.gps_deg_2_imformat(self.settings["Latitude"].get()))
        meta['longitude_im']= str(self.gps_deg_2_imformat(self.settings["Longitude"].get()))
        meta['bottomdepth']= str(self.settings["Depthtotal"].get())
        meta['dship_id']= str(self.settings["DShipID"].get())
        camera=str(self.settings["Camera"].get())
        cruise=str(self.settings["Cruise"].get())
        #yamlpath=os.path.dirname(image)+'/'+os.path.basename(os.path.dirname(image))+'.yaml'
        [camitem,yamlfile]=self.get_Camkey(meta,camera,cruise,yamlpath)
        return(camitem,yamlfile,meta)
        
    
    ## write exif thread
    def write_exif(self,ft,newimpath,uuid4):
        #print("ft: " +ft)
        if ft == "png":
            # if os.path.isfile(newimpath):
            #     # read file
                
            #     #write UUID to image meta data
            #     with open(newimpath, 'rb') as img_file:
            #         img = exIm(img_file)
            #         img.image_unique_id=uuid4
                    
            #     with open(newimpath, 'wb') as img_file2:
            #         img_file2.write(img.get_file())
            if os.path.isfile(newimpath):
                # read file
                #print("write pnginfo")
                #write UUID to image meta data
                
                targetImage = PngImageFile(newimpath)
                
                metadata = PngInfo()
                
                metadata.add_text("ImageUniqueID",uuid4)

                targetImage.save(newimpath, pnginfo=metadata)                        
                

        if ft == "jpg":
            if os.path.isfile(newimpath):
                # read file
                
                #write UUID to image meta data
                with open(newimpath, 'rb') as img_file:
                    img = exIm(img_file)
                    img.image_unique_id=uuid4
                    
                with open(newimpath, 'wb') as img_file2:
                    img_file2.write(img.get_file())
                
    #### get full path list

    def list_full_paths(self,directory):
        return [os.path.join(directory, file) for file in os.listdir(directory)]
    
    ### convert geps to decimal
    def gps_deg_2_dec(self,gps):

        gps_sp=gps.split(' ')
        if gps_sp[2]=='W':
            gps_dec='-'+ '{:08.4f}'.format(float(gps_sp[0][:-1])+float(gps_sp[1][:-1])/60)
        if gps_sp[2]=='E':
            gps_dec= '{:08.4f}'.format(float(gps_sp[0][:-1])+float(gps_sp[1][:-1])/60)  
        if gps_sp[2]=='N':
            gps_dec='{:07.4f}'.format(float(gps_sp[0][:-1])+float(gps_sp[1][:-1])/60)
        if gps_sp[2]=='S':
            gps_dec='-'+'{:07.4f}'.format(float(gps_sp[0][:-1])+float(gps_sp[1][:-1])/60)
        return(gps_dec)  
    
        ### convert geps to decimal
    def gps_deg_2_imformat(self,gps):

        gps_sp=gps.split(' ')
        if gps_sp[2]=='W':
            gps_dec='{:06.2f}'.format(float(gps_sp[0][:-1])+float(gps_sp[1][:-1])/60)+'W'
        if gps_sp[2]=='E':
            gps_dec= '{:06.2f}'.format(float(gps_sp[0][:-1])+float(gps_sp[1][:-1])/60)+'E'  
        if gps_sp[2]=='N':
            gps_dec= '{:05.2f}'.format(float(gps_sp[0][:-1])+float(gps_sp[1][:-1])/60)+'N'
        if gps_sp[2]=='S':
            gps_dec= '{:05.2f}'.format(float(gps_sp[0][:-1])+float(gps_sp[1][:-1])/60)+'S'

        return(gps_dec) 

    ### sort images by timestamp
    def imsorttime(self,x):
            
            try:
                ti=x[0:7]+x[9:14]

                return(int(ti))
                
            except ValueError:
                return(0)
            
    ## get hash file from saved image
    def get_hash(self,file):
        sha256_hash = hashlib.sha256()
        with open(file,"rb") as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096),b""):
                sha256_hash.update(byte_block)
            return(sha256_hash.hexdigest())        

    ## correct time mismatch
    def correct_time(self,im,type_cor):
         #2019-05-13 13:14:15.0000
        if type_cor==0:
            cortime=[]
            minstep=0
            hourstep=0
            daystep=0
            monthstep=0
            sek=int(im[13:15])-17
            if sek<0:
                sek=60+sek
                minstep=-1
            min=int(im[11:13]) -4 +minstep
            if min<0:
                min=60+min
                hourstep=-1
            hour=int(im[9:11]) -4 +hourstep
            if hour<0:
                hour=hour+24
                daystep=-1
            day=int(im[6:8]) + daystep
            if day==0:
                day=30 # April     
                monthstep=-1
            month=int(im[4:6])+  monthstep

            cortime.append(im[0:4]+"{:02.0f}{:02.0f}-{:02.0f}{:02.0f}{:02.0f}".format(month,day,hour,min,sek)+im[15:17])
            cortime.append(im[0:4]+"{:02.0f}{:02.0f}-{:02.0f}{:02.0f}{:02.0f}".format(month,day,hour,min,sek))
            return (cortime)
      
        if type_cor==1:
            cortime=[]
            minstep=0
            hourstep=0
            daystep=0
            monthstep=0
            
            min=int(im[11:13]) -4 
            if min<0:
                min=60+min
                hourstep=-1
            hour=int(im[9:11]) -4 +hourstep
            if hour<0:
                hour=hour+24
                daystep=-1
            day=int(im[6:8]) + daystep
            if day==0:
                day=30 # April     
                monthstep=-1
            month=int(im[4:6])+  monthstep
            print(im)
            print(im[0:4]+"{:02.0f}{:02.0f}-{:02.0f}{:02.0f}".format(month,day,hour,min))
            cortime.append(im[0:4]+"{:02.0f}{:02.0f}-{:02.0f}{:02.0f}".format(month,day,hour,min))
            cortime.append(im[0:4]+"{:02.0f}{:02.0f}-{:02.0f}{:02.0f}".format(month,day,hour,min))
            return (cortime)
    def get_uuid4():
        return(uuid.uuid4())

    ### Write Image Entry
    def update_Yaml(self,impath,camitem,yamlfile,meta,dateyaml,newpress,uuid4):
        pressurefactor=0.990102748343775
        imagename=os.path.basename(impath)
        newcamitem=camitem
        
        newcamitem['image-uuid']=deepcopy(uuid4)  
        newcamitem['image-hash']=self.get_hash(impath)
        newcamitem['image-datetime']= deepcopy(dateyaml)                                     #2019-05-13 13:14:15.0000
        #newcamitem['image-longitude']=deepcopy(float("{:09.5f}".format(float(meta['longitude_dec']))))
        #newcamitem['image-latitude']=deepcopy(float("{:09.5f}".format(float(meta['latitude_dec']))))
        #newcamitem['image-depth']=deepcopy(float("{:.2f}".format(float(newpress * pressurefactor))))
        newcamitem['image-longitude']=deepcopy(float(meta['longitude_dec']))
        newcamitem['image-latitude']=deepcopy(float(meta['latitude_dec']))
        newcamitem['image-depth']=deepcopy(float(newpress * pressurefactor))
        yamlfile['image-set-items'][imagename]=deepcopy(newcamitem)
        
        return (yamlfile)
    

        ### Write Image Entry
    def update_Yaml_Pipe(self,impath,camitem,yamlfile,meta,dateyaml,newpress,uuid4,hash):
        pressurefactor=0.990102748343775
        imagename=os.path.basename(impath)
        newcamitem=camitem
        
        newcamitem['image-uuid']=deepcopy(uuid4)  
        newcamitem['image-hash']=deepcopy(str(hash))
        newcamitem['image-datetime']= deepcopy(dateyaml)                                     #2019-05-13 13:14:15.0000
        #newcamitem['image-longitude']=deepcopy(float("{:09.5f}".format(float(meta['longitude_dec']))))
        #newcamitem['image-latitude']=deepcopy(float("{:09.5f}".format(float(meta['latitude_dec']))))
        #newcamitem['image-depth']=deepcopy(float("{:.2f}".format(float(newpress * pressurefactor))))
        newcamitem['image-longitude']=deepcopy(float(meta['longitude_dec']))
        newcamitem['image-latitude']=deepcopy(float(meta['latitude_dec']))
        newcamitem['image-depth']=deepcopy(float(newpress * pressurefactor))
        yamlfile['image-set-items'][imagename]=deepcopy(newcamitem)
        
        return (yamlfile)
    

    ### find matching profile
    def findmatching_timeprofile(self,Timefolders,timecorrection):
         tidiff=[]
         for times in Timefolders:
              if timecorrection:
                type_cor=1
                timecor=self.correct_time(os.path.basename(times),type_cor)[1]
                rightime=timecor
                tidiff.append(abs(int(timecor[0:8]+timecor[9:13])-int(self.settings["Datetimeprofile"].get()[0:8]+self.settings["Datetimeprofile"].get()[9:13])))
              else:
                rightime=os.path.basename(times)
                tidiff.append(abs(int(os.path.basename(times)[0:8]+os.path.basename(times)[9:13])-int(self.settings["Datetimeprofile"].get()[0:8]+self.settings["Datetimeprofile"].get()[9:13])))
         tidex= tidiff.index(min(tidiff))

         return(Timefolders[tidex],rightime)   

    #### save renamed image to new location

    def writeimage(self,imfol,image,newimagename,tarfolder,dfol,meta,ft,timeti,cruise,camera):
        
        #[newimfolderpthname,newimpath,imwritten]=self.writeimage(imgfol,image,newimagename,folder,dfol,meta,ft,dateti,camera,cruise)
        newimpathname=tarfolder+'/'+timeti[0:8]+"-"+timeti[9:13]+"_"+cruise+"_"+meta['dship_id']+"_"+camera+"_"+ft
        
        #print (newimpath)
        print(imfol + '/' +image,imfol + '/' + newimagename)
        if  image.endswith("."+ft):  
            #start = time.time()
            #print(imfol + '/' +image)
            print(imfol + '/' +image)
            try:
                os.rename(imfol + '/' +image,imfol + '/' + newimagename+'.'+ft)
                
            except:
                return(newimpathname,imfol+'/'+newimagename+'.'+ft,False) 
            
           
        return(newimpathname,imfol+'/'+newimagename+'.'+ft,True)
    
    
    def get_pressurefactor(self,oldpress,depthdata):
    
        dbpress=round(oldpress*10)
        startpress=depthdata[0,3]
        p=depthdata[:,3]
        if dbpress<startpress:
            return(depthdata[0,4]/startpress)
        else:
            ctdpress=np.reshape(p,(len(p),1))
            distance,index = spatial.KDTree(ctdpress).query(dbpress)
            return(depthdata[index,4]/depthdata[index,3])     
    
    
    def get_depthdata(self,ctdfile):
        #all_data= np.empty([6000,13]) #all_data[Station,Tiefe,Wert]
        #all_data[:] = np.nan

        #print(ctdfile)
        data_0 = np.loadtxt(ctdfile, skiprows = 121, dtype=float)
        #all_data[:np.shape(data_0)[0]]=data_0
        #all_data[i,np.shape(data_0)[0]:]=np.ma.masked
        return (data_0)
        # #reading variables out
        # time = all_data[:,0]
        # lon = all_data[:,:,1]
        # lat = all_data[:,:,2]
        # p = all_data[:,:,3]
        # z = all_data[:,:,4]

    ### get Basic Image Entry/ Write Station Entry
    def get_Camkey(self,meta,camera,cruise,yamlpath):
        yaml = ruamel.yaml.YAML(typ='safe', pure=True)
        #source_folder": self.source_folder,
        #     "target_folder": self.target_folder,
        #     "Datetimeprofile": self.Latitude,
        #     "Latitude": self.Latitude,
        #     "Longitude": self.Longitude,
        #     "DShipID": self.DShipID,
        #     "CTDprofileid": self.CTDprofileid,
        #     "Depthtotal": self.Depthtotal,
        #     "Depthprofile": self.Depthprofile,
        #     "Cameraframerate": self.Cameraframerate,
        #     "Cameraresolution": self.Cameraresolution,
        #     "Pixelpermm": self.Pixelpermm,
        #     "Flashduration": self.Flashduration,
        #     "Flashpower": self.Flashpower,
        #     "Tagamplitude": self.Tagamplitude,
        #     "Camera": self.Camera,
        #     "Cruise": self.Cruise,
        #     "Platform": self.Platform,
        ### put here path to Basic YAML File 
        if self.settings["mirror_adjusted"]:
            mirror_adjusted_str="yes"
        else:
            mirror_adjusted_str="no" 
                     

        Imageaquisition= "Flashduration "+ self.settings["Flashduration"].get() + ", Flashpower " + self.settings["Flashpower"].get() + ", Tagamplitude " + self.settings["Tagamplitude"].get() +", Binning " + self.settings["Binning"].get() +", Gain " + self.settings["Gain"].get()+", Mirrow adjusted " + mirror_adjusted_str + ", Lenssystem " + self.settings["Lenssystem"].get()
    
        if not os.path.isfile(yamlpath):
            root_dir = Path(__file__).resolve().parent.parent
            yamlfilnm=root_dir / "Yamlbase.yaml"
            with open(yamlfilnm) as fp:
                data = yaml.load(fp)
                data['image-set-header']['image-set-name']=deepcopy(meta['dship_id']+"_"+camera)        
                data['image-set-header']['image-set-event']=deepcopy(meta['dship_id']) 
                data ['image-set-header']['image-set-uuid']=str(uuid.uuid4())                     
                data['image-set-header']['image-set-platform']=deepcopy(self.settings["Platform"].get())
                data['image-set-header']['image-set-event-information']=deepcopy(self.settings["Comment"].get())
                data['image-set-header']['image-set-acquisition-settings']=deepcopy(Imageaquisition)
                data['image-set-header']['image-set-sensor']=deepcopy(camera)  
                data['image-set-header']['image-set-project']=deepcopy(self.settings["Cruise"].get())
                data['image-set-header']['image-set-pixel-per-millimeter']=deepcopy(self.settings["Pixelpermm"].get())
                
                
                camitem=data['image-set-items']['SO268-1_21-1_GMR_CAM-23_20190513_131415.jpg']
                data['image-set-items'].pop('SO268-1_21-1_GMR_CAM-23_20190513_131415.jpg', None)
        # else:
        #     with open(yamlpath) as fp:
        #         data = yaml.load(fp)
                
                
                
        #         camitem=data['image-set-items'][next(iter(data['image-set-items']))]
                
        return(camitem,data)