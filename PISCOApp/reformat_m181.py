import tkinter as tk
import customtkinter as ctk
from tkinter.filedialog import askdirectory
import pandas as pd
import os.path
def list_full_paths(directory):
        return [os.path.join(directory, file) for file in os.listdir(directory)]
### convert geps to decimal
def gps_deg_2_dec(gps):
        print(gps)
        gps_sp=gps
        if gps_sp[32]=='W':
            gps_lon='-'+ '{:07.3f}'.format(float(gps_sp[26:29])+float(gps_sp[30:32])/60)
        if gps_sp[32]=='E':
            gps_lon= '{:07.3f}'.format(float(gps_sp[26:29])+float(gps_sp[30:32])/60)  
        if gps_sp[24]=='N':
            gps_lat='{:06.3f}'.format(float(gps_sp[19:21])+float(gps_sp[22:24])/60)
        if gps_sp[24]=='S':
            gps_lat='-'+'{:06.3f}'.format(float(gps_sp[19:21])+float(gps_sp[22:24])/60)
        return(gps_lat,gps_lon) 



folder= askdirectory()

profiles=list_full_paths(folder)

for profil in profiles:
    df=pd.read_csv(profil)
    [lat,lon]=gps_deg_2_dec(os.path.basename(profil))
    latlist=[]
    lonlist=[]
    Datelist=[]
    Timelist=[]
    Profilelist=[]
    for x in range(len(df)):
         latlist.append(lat)
         lonlist.append(lon)
         Datelist.append(os.path.basename(profil)[34:42])
         Timelist.append(os.path.basename(profil)[43:47])
         Profilelist.append(os.path.basename(profil)[15:18])
    df.pop('Profile ID')
    df.pop('Date/Time [YYYYMMDD-HHMM]')
    df.insert(0, "Profile ID", Profilelist, True)
    df.insert(1, "Latitude", latlist, True)
    df.insert(2, "Longitude", lonlist, True)
    df.insert(3, "Date [YYYYMMDD]", Datelist, True)
    df.insert(3, "Time [HHMM]", Timelist, True)

    df.to_csv('/home/pisco-controller/Desktop/M181-Brasil/'+os.path.basename(profil))







