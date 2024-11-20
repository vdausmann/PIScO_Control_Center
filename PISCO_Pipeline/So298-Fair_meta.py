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

import yaml
import ruamel.yaml
from copy import deepcopy
import hashlib
import uuid
from exif import Image as exIm
yaml = ruamel.yaml.YAML()
#import darknet as dn



camera ="PISCO1" 
cruise="HE570"

# Pressurefactor Average from HE570 CTD Data ("HE570_Druckfaktor.csv")
pressurefactor=0.990102748343775


###Write YAML Functions

########################################################################################################

### get Basic Image Entry/ Write Station Entry
def get_Camkey(meta,camera,cruise):

    ### put here path to Basic YAML File    
    with open(r'/home/pisco-controller/Desktop/PISCO_Software/PISCO_Pipeline/Yamlbase.yaml') as fp:
        data = yaml.load(fp)
        data['image-set-header']['image-set-name']=deepcopy(cruise+"_{:03.0f}_".format(meta['dship_id'] )+camera)        
        data['image-set-header']['image-set-event']=deepcopy(cruise+"_"+str(meta['dship_id']) )
        data ['image-set-header']['image-set-uuid']=str(uuid.uuid4())
        
         
        
        
        camitem=data['image-set-items']['SO268-1_21-1_GMR_CAM-23_20190513_131415.jpg']
        data['image-set-items'].pop('SO268-1_21-1_GMR_CAM-23_20190513_131415.jpg', None)
        return(camitem,data)


### Write Image Entry

def update_Yaml(impath,camitem,yamlfile,meta,dateyaml,newpress,uuid4):
      
      imagename=os.path.basename(impath)
      newcamitem=camitem
      
      newcamitem['image-uuid']=deepcopy(uuid4)  
      newcamitem['image-hash']=get_hash(impath)
      newcamitem['image-datetime']= deepcopy(dateyaml)                                     #2019-05-13 13:14:15.0000
      newcamitem['image-longitude']=deepcopy(float("{:09.5f}".format(meta['longitude_dec'])))
      newcamitem['image-latitude']=deepcopy(float("{:09.5f}".format(meta['latitude_dec'])))
      newcamitem['image-depth']=deepcopy(float("{:.2f}".format(newpress * pressurefactor)))
      yamlfile['image-set-items'][imagename]=deepcopy(newcamitem)
      
      return (yamlfile)


## get hash file from saved image

def get_hash(file):
    sha256_hash = hashlib.sha256()
    with open(file,"rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096),b""):
            sha256_hash.update(byte_block)
        return(sha256_hash.hexdigest())


##
def get_uuid4():
    return(uuid.uuid4())


############################################################################################################



### sort images by timestamp

def imsorttime(x):

    
        
        try:
            ti=x[0:7]+x[9:14]

            return(int(ti))
            
        except ValueError:
            return(0)
    

### convert geps to decimal
def gps_deg_2_dec(gps):

    gps_sp=gps.split(' ')
    if gps_sp[2]=='W':
        gps_dec='-'+ gps_sp[0][:-1]+'.'+str(float(gps_sp[1][:-1])/60)+'deg'
    if gps_sp[2]=='E':
        gps_dec='+'+ gps_sp[0][:-1]+'.'+str(float(gps_sp[1][:-1])/60)+'deg'  
    if gps_sp[2]=='N':
        gps_dec='+'+ gps_sp[0][:-1]+'.'+str(float(gps_sp[1][:-1])/60)+'deg'
    if gps_sp[2]=='S':
        gps_dec='-'+ gps_sp[0][:-1]+'.'+str(float(gps_sp[1][:-1])/60)+'deg' 

    return(gps_dec)             



### find matching metadata

def findmatchingmeta(imagefoldername,metagps):
    
    im = imagefoldername
    timekeyim=int(im[0:7]+im[9:12])
    
    
    tidiff=[]
    Piscolist=pd.read_csv('/home/pisco-controller/Desktop/Metadaten_rename_script/So298-Piscostationlist.csv')

    for x in range ( len(metagps['Event Time']) ):
        if metagps['Device Operation'][x] in Piscolist['Station-ID']:
            #tidiff.append(abs(int(metagps['Event Time'][x][0:4]+metagps['Event Time'][x][5:7]+metagps['Event Time'][x][8:10]+metagps['Event Time'][x][11:13]+metagps['Event Time'][x][14:16])-timekeyim)
            tidiff.append(abs(int(metagps['Event Time'][x])-timekeyim))
    tidex= tidiff.index(min(tidiff)) 

    for y in range ( len(Piscolist['Station-ID']) ):
        if metagps['Device Operation'][tidex] == Piscolist['Station-ID'][y]:
            profileid=Piscolist['Ctd-profile'][y]

    metall={}
    metall['profileid']= profileid  
    metall['latitude_dec']= gps_deg_2_dec(metagps['Latitude'] [tidex])
    metall['longitude_dec']= gps_deg_2_dec(metagps['Longitude'] [tidex])
    metall['bottomdepth']= metagps['Depth (m)'] [tidex]
    metall['dship_id']= metagps['Device Operation'] [tidex]
    
    ### get min and max pressure to select images
    #startprof=metapressure[metall['profileid']]['pressure'].index(min(metapressure[metall['profileid']]['pressure'])) 
    #stopprof=metapressure[metall['profileid']]['pressure'].index(max(metapressure[metall['profileid']]['pressure'])) 
    #stopprof=len(metapressure[metall['profileid']]['pressure'])-3
    
    
    
    return(metall)


#### change meta time to int
def mettimekey(mettime):
    me=str(mettime)
    inttime=int(me[11:13]+me[14:16]+me[17:19]+'00' )
    return(inttime)
    

#### interpolate Pressure interpolatepressure(nearest timestamp before cameratime,nearest timestamp after cameratime,cameratime,pressure before(nearest timestamp before cameratime),press (nearest timestamp after cameratime +1second)):   

def interpolatepressure(mettimekeylow,mettimekeyhigh,camtimekeyim,presslow,presshigh):   
    #print('prelow prehi camtimekeyim mettimekeyhigh mettimekeylow')
    #print(presslow)
    #print(presshigh)
    #print(camtimekeyim)
    #print(mettimekeyhigh)
    #print(mettimekeylow)
    pressinterpol=float(presslow)+((float(presshigh)-float(presslow))*((camtimekeyim-mettimekeylow)/(mettimekeyhigh-mettimekeylow)))
    
    return(pressinterpol)
    
#### save renamed image to new location

def writeimage(imfol,image,newimagename,tarfolder,dfol,meta,ft):
    
    newimpath=tarfolder+'/'+os.path.basename(image)[0:8]+"_"+cruise+"_{:03.0f}".format(meta['dship_id'])+"_"+camera+"_"+ft
    
    print (newimpath)
    if not os.path.exists(newimpath):
        os.makedirs(newimpath)
    if  image.endswith(".tif"):  
        start = time.time()
        #print(imfol + '/' +image)
        try:
            im = Image.open(imfol + '/' +image)
        except:
            return(newimpath,newimpath+'/'+newimagename+'.'+ft,False) 
        
        
        im.save(newimpath+'/'+newimagename+'.'+ft, ft)
        #im.save(newimpathjpg+'/'+newimagename+'.jpg', "jpg")
        print("time open and saveing image")
        end = time.time()
        print(end - start)    
    return(newimpath,newimpath+'/'+newimagename+'.'+ft,True)
#### rename images

def renameimages(folder,tarfolder,metagps):
    
    datefolder=list_full_paths(folder)
    ImSaverrorls=[]
    
    for dfol in datefolder:
        print(os.path.basename(dfol))
        if os.path.basename(dfol).startswith("2023") :
        #if os.path.basename(dfol).startswith("2021"):
            imagefolder= list_full_paths(dfol)
            
            
            for imfol in imagefolder:
              datformatfolders=  list_full_paths(imfol)
              for imgfol in imfol:
                imfiles=os.listdir(imgfol)
                meta=findmatchingmeta(os.path.basename(imfol),metagps)
                
                print ('Start renaming of: ' +os.path.basename(imfol) )
                pressin=0
                imwritten=False  
                #print(time)
                #print(press)
                ## set yamlbasic
                [camitem,yamlfile]=get_Camkey(meta)    
                    
                yamwrite=False
                startsort=True
                png="png"
                jpg="jpg"
                filetypes=[png,jpg]
                for ft in filetypes:

                    for image in sorted(imfiles, key = imsorttime):
                        if image.endswith('.tif'):
                            im = os.path.basename(image)[:-4]
                            newpress=float(image[18:25])*10
                            
                            #2019-05-13 13:14:15.0000
                            dateyaml=im[0:4]+'-'+im[4:6]+'-'+im[6:8]+' '+im[9:11]+':'+im[11:13]+':'+im[13:15]+"."+im[15:17]
                            
                            
                            newimagename=cruise+"_{:03.0f}".format(meta['dship_id'])+"_"+camera+"_{:07.2f}dbar-{:05.2f}lat-{:06.2f}lon_".format(newpress,meta['latitude_dec'],meta['longitude_dec'] )+dateti
                            [newimfolderpth,newimpath,imwritten]=writeimage(imfol,image,newimagename,tarfolder,dfol,meta,ft)

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
                                                    yamfile=update_Yaml(newimpath,camitem,yamlfile,meta,dateyaml,newpress,uuid4)
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
                                                    img.write(img.get_file())
                                                
                                                with open(newimpath, 'rb') as img_file:
                                                    img2 = exIm(img_file)

                                                    if img.get("image_unique_id")==uuid4:
                                                    #update yaml file
                                                        yamfile=update_Yaml(newimpath,camitem,yamlfile,meta,dateyaml,newpress,uuid4)
                                                        yamwrite=True
                                                    else:
                                                        print('UUID JPG Metadatawrite Error!')            
                                        
                    if yamwrite:
                        
                        with open(newimfolderpth+'/'+os.path.basename(newimfolderpth)+'.yaml','w') as newyamlfile:
                                yaml.dump(yamfile, newyamlfile)                
                    
                    print('Could not rename following images: \n')    
                    for imerror in ImSaverrorls:
                        
                        print(imerror+'\n')


#### read specific metadata for he570
def readmetadata():
    
    gpsmeta=pd.read_csv("/home/pisco-controller/Desktop/ctd3004-4.dat",sep=';',encoding = "ISO-8859-1")
    
    
    return (gpsmeta)

#### get full path list

def list_full_paths(directory):
    return [os.path.join(directory, file) for file in os.listdir(directory)]
 



####### Main Programm    
def main():
    
    print ("Choose Image Folder (Basic Folder contaning all Date Folders) !")
    folder=""
    folder = askdirectory()
    print ("Choose Target Folder (Basic Folder where all renamed Date Folders will be saved) !")
    tarfolder=""
    tarfolder = askdirectory()
    [metagps]=readmetadata()
    renameimages(folder,tarfolder,metagps)

main()