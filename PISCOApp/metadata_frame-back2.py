import tkinter as tk
import customtkinter as ctk
from tkinter.filedialog import askdirectory

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
from PIL import Image
from PIL.PngImagePlugin import PngImageFile, PngInfo
import yaml
import ruamel.yaml
from copy import deepcopy
import hashlib
import uuid
from exif import Image as exIm



class MetadataFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # setting variables
        self.source_folder = tk.StringVar(self, "") 
        self.target_folder = tk.StringVar(self, "") 
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
        

        self.settings = {
            "source_folder": self.source_folder,
            "target_folder": self.target_folder,
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
            
            
        }

        # source folder
        ctk.CTkLabel(self, text="Set Source folder:").grid(row=0, column=0)
        ctk.CTkButton(
            self,
            text="Choose folder",
            width=100,
            command=lambda: self.choose_folder(self.source_folder),
        ).grid(row=1, column=0, pady=5, padx=5)
        print(self.settings["source_folder"].get())
        ctk.CTkLabel(self, text="Source folder:").grid(row=4, column=5)
        ctk.CTkLabel(self, text=self.settings["source_folder"].get()).grid(row=5, column=5)
        # # target folder
        # ctk.CTkLabel(self, text="Target folder:").grid(row=0, column=0)
        # ctk.CTkButton(
        #     self,
        #     text="Choose folder",
        #     width=100,
        #     command=lambda: self.choose_folder(self.target_folder),
        # ).grid(row=1, column=0, pady=5, padx=5)

       
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

    def rename_imgs(self):
        yaml = ruamel.yaml.YAML()
        folder=self.settings["source_folder"].get()
        tarfolder=self.target_folder
        pressurefactor=0.990102748343775
        
        print(str(self.settings["Latitude"].get()))
        print(len(str(self.settings["Latitude"].get())))
        print(len(self.settings["Latitude"].get()))
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
        
        for dfol in datefolder:
            print(os.path.basename(dfol))
            if os.path.basename(dfol)==self.settings["Datetimeprofile"].get()[0:8] :
            #if os.path.basename(dfol).startswith("2021"):
                Timefolders= self.list_full_paths(dfol)
                imfolli=self.findmatching_timeprofile(Timefolders)
                
                
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
                    for fit in filetypes:

                        for image in sorted(imfiles, key = self.imsorttime):
                            if image.endswith('.tif') or image.endswith('.png') or image.endswith('.jpg'):
                                if image.endswith('.png'):
                                     ft="png"
                                if image.endswith('.jpg'):
                                     ft="jpg"     
                                im = os.path.basename(image)[:-4]
                                newpress=float(image[18:25])*10
                                
                                newimfolderpth=imgfol

                                #2019-05-13 13:14:15.0000
                                oldtime=im[0:17]
                                dateti=self.correct_time(oldtime)

                                #dateti=im[0:17]
                                dateyaml=dateti[0:4]+'-'+dateti[4:6]+'-'+dateti[6:8]+' '+dateti[9:11]+':'+dateti[11:13]+':'+dateti[13:15]+"."+dateti[15:17]
                                
                                #dateti=im[0:17]
                                
                                newimagename=cruise+"_"+meta['dship_id']+"_"+camera+"_{:07.2f}dbar-".format(newpress)+meta['latitude_im']+"-"+meta['longitude_im']+"_"+dateti
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
                                            
                                            
                                            
                                            if ft == "png":
                                                if os.path.isfile(newimpath):
                                                    # read file
                                                    
                                                    #write UUID to image meta data
                                                    targetImage = PngImageFile(newimpath)
                                                    uuid4=str(uuid.uuid4())
                                                    metadata = PngInfo()
                                                    
                                                    metadata.add_text("ImageUniqueID",uuid4)

                                                    targetImage.save(newimpath, pnginfo=metadata)                        
                                                    targetImage = PngImageFile(newimpath)
                                                    
                                                    if targetImage.text['ImageUniqueID']==uuid4:
                                                    #update yaml file
                                                        yamfile=self.update_Yaml(newimpath,camitem,yamlfile,meta,dateyaml,newpress,uuid4)
                                                        yamwrite=True
                                                    else:
                                                        print('UUID PNG Metadatawrite Error!')
                                            if ft == "jpg":
                                                if os.path.isfile(newimpath):
                                                    # read file
                                                    uuid4=str(uuid.uuid4())
                                                    #write UUID to image meta data
                                                    with open(newimpath, 'rb') as img_file:
                                                        img = exIm(img_file)
                                                        img.image_unique_id=uuid4
                                                        
                                                    with open(newimpath, 'wb') as img_file2:
                                                        img_file2.write(img.get_file())
                                                    
                                                    with open(newimpath, 'rb') as img_file:
                                                        img2 = exIm(img_file)

                                                        if img2.get("image_unique_id")==uuid4:
                                                        #update yaml file
                                                            yamfile=self.update_Yaml(newimpath,camitem,yamlfile,meta,dateyaml,newpress,uuid4)
                                                            yamwrite=True
                                                        else:
                                                            print('UUID JPG Metadatawrite Error!')            
                                            
                        if yamwrite:
                            
                            with open(imgfol+'/'+os.path.basename(newimfolderpthname)+'.yaml','w') as newyamlfile:
                                    yaml.dump(yamfile, newyamlfile)                
                        
                        print('Could not rename following images: \n')    
                        for imerror in ImSaverrorls:
                            
                            print(imerror+'\n')

                    os.rename(imgfol,newimfolderpthname)
            os.rename(imfolli,dfol + os.path.basename(newimfolderpthname)[:-4])    

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
    def correct_time(self,im):
         #2019-05-13 13:14:15.0000
        
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

        cortime=im[0:4]+"{:02.0f}{:02.0f}-{:02.0f}{:02.0f}{:02.0f}".format(month,day,hour,min,sek)+im[15:17]
        return (cortime)
    ##
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
    
    ### find matching profile
    def findmatching_timeprofile(self,Timefolders):
         tidiff=[]
         for times in Timefolders:
              tidiff.append(abs(int(os.path.basename(times)[0:8]+os.path.basename(times)[9:13])-int(self.settings["Datetimeprofile"].get()[0:8]+self.settings["Datetimeprofile"].get()[9:13])))
         tidex= tidiff.index(min(tidiff))
         return(Timefolders[tidex])   

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


    ### get Basic Image Entry/ Write Station Entry
    def get_Camkey(self,meta,camera,cruise):

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

        Imageaquisition= "Flashduration: "+ self.settings["Flashduration"].get() + ", Flashpower: " + self.settings["Flashpower"].get() + ", Tagamplitude: " + self.settings["Tagamplitude"].get() +", Binning: " + self.settings["Binning"].get() +", Gain: " + self.settings["Gain"].get()
        with open(r'/home/pisco-controller/Desktop/PISCO_Software/PISCO_Pipeline/Yamlbase.yaml') as fp:
            data = yaml.load(fp)
            data['image-set-header']['image-set-name']=deepcopy(cruise+"_"+meta['dship_id']+"_"+camera)        
            data['image-set-header']['image-set-event']=deepcopy(cruise+"_"+meta['dship_id']) 
            data ['image-set-header']['image-set-uuid']=str(uuid.uuid4())                     
            data['image-set-header']['image-set-platform']=deepcopy(self.settings["Platform"].get())
            data['image-set-header']['image-set-event-information']=deepcopy(self.settings["Comment"].get())
            data['image-set-header']['image-set-acquisition-settings']=deepcopy(Imageaquisition)
            data['image-set-header']['image-set-sensor']=deepcopy(camera)  
            data['image-set-header']['image-set-project']=deepcopy(self.settings["Cruise"].get())
            data['image-set-header']['image-set-pixel-per-millimeter']=deepcopy(self.settings["Pixelpermm"].get())
            
            
            camitem=data['image-set-items']['SO268-1_21-1_GMR_CAM-23_20190513_131415.jpg']
            data['image-set-items'].pop('SO268-1_21-1_GMR_CAM-23_20190513_131415.jpg', None)
            return(camitem,data)