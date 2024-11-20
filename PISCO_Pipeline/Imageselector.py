import os
import numpy as np
import pandas as pd
import cv2 as cv

import cv2
import numpy as np
from tkinter.filedialog import askdirectory,askopenfilename



def safe_sampleimgs(img_path,csv_path):
    df=pd.read_csv(csv_path)
    index_ob=df[df.esd>3500].index
    im_dict={"filename":[],"time":[]}
    imlist_all=os.listdir(img_path)
    for im in imlist_all:
        if im.endswith('.jpg') or im.endswith('.png'):
            im_dict['filename'].append(im)
            im_dict['time'].append(os.path.basename(im).split("_")[4][:-4])
    im_df=pd.DataFrame.from_dict(im_dict)
    for ind in index_ob:
        x=int(df.iloc[ind]["x"])
        y=int(df.iloc[ind]["y"])
        w=int(df.iloc[ind]["w"])
        h=int(df.iloc[ind]["h"])
        t=df.iloc[ind]["date-time"]

        #time_ind=im_df.time[im_df.time == t].index
        offset=40
        time_ind=im_df.time[im_df.time == t].index.tolist()[0]
        im_path=im_df.iloc[time_ind]['filename']
        img = cv2.imread(os.path.join(img_path,im_path))
        if int(df.iloc[ind]['esd'])>50000:
            crop=img
            cropped=False
        else:
            cropped=True
            if y-(int(h/2)+offset)<0:
                y_1=0
            else:
                y_1=y-(int(h/2)+offset)
            if  y+int(h/2)+offset>2559:
                y_2=2559
            else:
                y_2= y+int(h/2)+offset      
            if x-(int(w/2)+offset)<0:
                x_1=0
            else:
                x_1=x-(int(w/2)+offset)
            if  x+int(w/2)+offset>2559:
                x_2=2559
            else:
                x_2= x+int(w/2)+offset          
            crop=img[y_1:y_2,x_1:x_2]
        
        #crop=apply_brightness_contrast(crop,45,45) 
        crop=contrast_morph(crop)    
        crop= apply_brightness_contrast(crop,25,35)
        # font 
        font = cv2.FONT_HERSHEY_SIMPLEX   
        # org 
              
        # fontScale 
                
        # Blue color in BGR 
        color = (0, 0, 0)        
        # Line thickness of 2 px 
        thickness = 2        
        # Using cv2.putText() method 
        if cropped:
            fontScale = 0.5
            thickness = 1
            org = (5, 30) 
            orgline=(5,40)
            endline=(51,40)  
            cv2.putText(crop, '1mm '+ str(df.iloc[ind]["pressure [dbar]"])+'[dbar]', org, font,  
                        fontScale, color, thickness, cv2.LINE_AA) 
            cv2.line(crop,orgline,endline,(0,0,0),3) 
            #im_savename=os.path.basename(im_path)[:-4]+'_'+str(df.iloc[ind]["crop_index"])+'.jpg'
            im_savename=os.path.basename(im_path)[:-4]+'_'+str(df.iloc[ind]["index"])+'.jpg'

        else:
            fontScale = 2
            thickness = 4
            org = (2500, 1000) 
            orgline=(2530,1000)
            endline=(2530,1435)  
            cv2.putText(crop, '1cm '+ str(df.iloc[ind]["pressure [dbar]"])+'[dbar]', org, font,  
                        fontScale, color, thickness, cv2.LINE_AA) 
            cv2.line(crop,orgline,endline,(0,0,0),10)
            im_savename=os.path.basename(im_path)[:-4]+'.jpg'

        
        

        if df.iloc[ind]["pressure [dbar]"]<50:
            fol_50 = img_path+'_SampleImgs/50m'
            os.makedirs(fol_50, exist_ok=True)
            croppath=os.path.join(fol_50,im_savename)
            cv2.imwrite(croppath,crop)
            print(croppath)
        elif df.iloc[ind]["pressure [dbar]"]>50 and df.iloc[ind]["pressure [dbar]"]<500:
            #fol_50_500 = os.path.join(os.path.dirname(img_path),'SampleImgs/50-500m')
            fol_50_500 = img_path+'_SampleImgs/50-500m'
            os.makedirs(fol_50_500, exist_ok=True)
            croppath=os.path.join(fol_50_500,im_savename)
            cv2.imwrite(croppath,crop)
            print(croppath)
        elif df.iloc[ind]["pressure [dbar]"]>500 :
            fol_500_bottom = img_path+'_SampleImgs/500m-bottom'
            os.makedirs(fol_500_bottom, exist_ok=True)
            croppath=os.path.join(fol_500_bottom,im_savename)
            cv2.imwrite(croppath,crop)
            print(croppath)    

def contrast_morph(img):
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE,(17,17))
    # Top Hat Transform
    topHat = cv.morphologyEx(img, cv.MORPH_TOPHAT, kernel)# Black Hat Transform
    blackHat = cv.morphologyEx(img, cv.MORPH_BLACKHAT, kernel)
    res = img + topHat - blackHat
    return(res)


def apply_brightness_contrast(input_img, brightness = 0, contrast = 0):
    
    if brightness != 0:
        if brightness > 0:
            shadow = brightness
            highlight = 255
        else:
            shadow = 0
            highlight = 255 + brightness
        alpha_b = (highlight - shadow)/255
        gamma_b = shadow
        
        buf = cv2.addWeighted(input_img, alpha_b, input_img, 0, gamma_b)
    else:
        buf = input_img.copy()
    
    if contrast != 0:
        f = 131*(contrast + 127)/(127*(131-contrast))
        alpha_c = f
        gamma_c = 127*(1-f)
        
        buf = cv2.addWeighted(buf, alpha_c, buf, 0, gamma_c)

    return buf

# print("Select Image Dir!")
# imgs_dir= askdirectory()
# print("Select meta_dataframe.csv!")
# data_csv= askopenfilename()
# safe_sampleimgs(imgs_dir,data_csv)
