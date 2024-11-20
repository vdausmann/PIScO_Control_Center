import os
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('agg')
from tkinter.filedialog import askdirectory,askopenfilename


from pandas.errors import EmptyDataError

import matplotlib.colors as mcolors

def read_taglog(df_timepress,path):
    templist={"Index":[],"Time":[],"Lockstate":[],"Frequency":[],"Amplitude":[],"Current":[],"phase":[],"Voltage":[],"Power":[],"ImgPower":[]}
    with open(path,"+r") as f:
        Lines=f.readlines()
        tt=False
        lasttime=0
        rows=["Lockstate","Amplitude","Frequency","Current","Voltage","phase","Power","ImgPower"]
        y=0
        for line in Lines:
            if line[0:2]=='20':
                #print(line)
                entrys=line.split(':')
                time=int(entrys[0][0:4]+entrys[0][5:7]+entrys[0][8:10]+entrys[0][-2:]+entrys[1]+entrys[2][0:2])
                if time != lasttime:
                    lasttime=time
                    templist["Time"].append(time)
                    x=3
                    templist["Index"].append(y)
                    y=y+1
                    for row in rows:
                        #print(entrys[x].split(' ')[1])
                        templist[row].append(float(entrys[x].split(' ')[1]))
                        x=x+1
    df_time_data=pd.DataFrame.from_dict(templist) 
    taglist_press={"pressure [dbar]":[],"Index":[],"Time":[],"Lockstate":[],"Frequency":[],"Amplitude":[],"Current":[],"phase":[],"Voltage":[],"Power":[],"ImgPower":[]}                   
    x=0
    rows=["Time","Lockstate","Amplitude","Frequency","Current","Voltage","phase","Power","ImgPower"]
    for timeind in df_timepress["Index"]:
        if df_time_data.Time[df_time_data.Time==df_timepress.iloc[timeind]["time"]].index.tolist() != []:
            press_index=df_time_data.Time[df_time_data.Time==df_timepress.iloc[timeind]["time"]].index.tolist()[0]
            taglist_press["pressure [dbar]"].append(df_timepress.iloc[timeind]["press"])
            taglist_press["Index"].append(x)
            x=x+1
            for row in rows:
                taglist_press[row].append(df_time_data.iloc[press_index][row])
    df_taglog=pd.DataFrame.from_dict(taglist_press)             
    return(df_taglog)

def read_templog(path):
    templist={"Index":[],"Time":[],"TT":[],"T1":[],"T2":[],"C1":[],"C2":[],"TH":[]}
    with open(path,"+r") as f:
        Lines=f.readlines()
        tt=False
        z=0
        rows=["Index","Time","TT","T1","T2","C1","C2","TH"]
        for x in range( len(Lines)-2):
            ind=Lines[x].split('_')
            ind2=Lines[x+1].split('_')

            if ind[0][0:2]=='20' and ind2[0][-2:]=='TT':
                #if int(ind[0]+ind[1][:-1]+ind[2][:-1]+ind[3][:-2])<time_max:
                    try:
                        templist["Index"].append(z)    
                        templist["Time"].append(int(ind[0]+ind[1][:-1]+ind[2][:-1]+ind[3][:-2]))
                        templist["TT"].append(float(ind2[1]))
                        templist["T1"].append(float(ind2[3]))
                        templist["T2"].append(float(ind2[5]))
                        templist["C1"].append(float(ind2[7]))
                        templist["C2"].append(float(ind2[9]))
                        templist["TH"].append(float(ind2[11][:-2]))
                        z=z+1
                    except:
                        rowmin=300000

                        for row in rows:
                            if len(templist[row])<rowmin:
                                rowmin=len(templist[row])
                        for row in rows:
                            if len(templist[row])>rowmin:
                                templist[row].pop()                   


                        pass    
            
                
    rows=["Index","Time","TT","T1","T2","C1","C2","TH"]
    for leni in rows:
        print(leni+' : '+str(len(templist[leni])))
    return(templist)

def timesort(file):
    try:
        return (int(file.split("_")[4][:8]+file.split("_")[4][9:17] ))
    except IndexError:
        return (int(file.split("_")[0][:8]+file.split("_")[0][9:17] ))

def time_to_press(file_path,templogpath):
    imlist_all=os.listdir(file_path)
    imlist=[]
    for im in imlist_all:
        if im.endswith('.jpg') or im.endswith('.png') or im.endswith('.tif'):
            imlist.append(os.path.basename(im))
    #imlist=imlist_unsorted.sort(key=timesort)
    #imlist.sort(key=timesort,reverse=True)
    print(imlist[0])
    imlist.sort(key=timesort)
    
    #imlist_timemax=int(imlist[len(imlist)-1].split("_")[4][:8]+imlist[len(imlist)-1].split("_")[4][9:15] )
    time_data=read_templog(templogpath)
    y=0
    dist=10000000
    timepress={'Index':[],'time':[],'press':[]}
    second=0
    ind=0
    for im in imlist:
        try:
            time=int(im.split("_")[4][:8]+im.split("_")[4][9:15] )
        except IndexError:
            time=int(im.split("_")[0][:8]+im.split("_")[0][9:15] )
        try: 
            press=float(im.split("_")[3][:7])
        except IndexError:
            press=float(im.split("_")[1][:7])
        if time != second:
            second=time
            timepress['Index'].append(ind)
            timepress['time'].append(time)
            timepress["press"].append(press)
            ind=ind+1
    df_timepress=pd.DataFrame.from_dict(timepress)
    df_time_data=pd.DataFrame.from_dict(time_data)
    
    templist_press={"Index":[],"Time":[],"TT":[],"T1":[],"T2":[],"C1":[],"C2":[],"TH":[],"pressure [dbar]":[]}
    x=0
    rows=["Time","TT","T1","T2","C1","C2","TH"]
    for timeind in df_timepress["Index"]:
        if df_time_data.Time[df_time_data.Time==df_timepress.iloc[timeind]["time"]].index.tolist() != []:
            press_index=df_time_data.Time[df_time_data.Time==df_timepress.iloc[timeind]["time"]].index.tolist()[0]
            templist_press["pressure [dbar]"].append(df_timepress.iloc[timeind]["press"])
            templist_press["Index"].append(x)
            x=x+1
            for row in rows:
                templist_press[row].append(df_time_data.iloc[press_index][row])
    
    rows=["Time","TT","T1","T2","C1","C2","TH","pressure [dbar]"]
    for leni in rows:
        print(leni+' : '+str(len(templist_press[leni])))
    df_templist_press=pd.DataFrame.from_dict(templist_press)            

    station_id=imlist[0].split("_")[0]+"_"+imlist[0].split("_")[1]
 
    return(df_templist_press,station_id,df_timepress)            


def plot_templog(df,stationID, plot_path:str, preliminary=True, depth_min=0,):

    fig, ax1 = plt.subplots(figsize=(10,15))
    fig.subplots_adjust(top=0.97) # Adjust the value as needed
    fig.subplots_adjust(bottom=0.2)

    ax1.invert_yaxis()

    ax2 =ax1.twiny()
    ax3 =ax1.twiny()
    ax4 =ax1.twiny()
    ax5 =ax1.twiny()
    ax6 =ax1.twiny()
   # ax7 =ax1.twiny()

    axes = [ax1,ax2,ax3,ax4,ax5,ax6]
    temp = ["TT","T1","T2","C1","TH","pressure [dbar]"]
    Tempr_names = ['Tag-Tempr. Mean','Tag-Tempr. 1','Tag-Tempr. 2','PC Tempr. 1','Heating Tempr']
    colors = ['red', 'blue', 'lime', 'cyan', 'black']
    positions = [0,40,80,120,160]

    #df.set_index("pressure [dbar]", inplace=True)
    for ax,i,name,color,pos in zip(axes,temp,Tempr_names,colors,positions):
        if i in df.columns:
            ax.plot(df[i], df["pressure [dbar]"] , color=color, label=name)
            ax.set_xlabel(f' {name} [C]',color=color)
            ax.spines['bottom'].set_color(color)
            ax.tick_params(axis='x', colors=color)
            ax.spines['top'].set_visible(False)
            ax.spines['bottom'].set_position(('outward', pos))
            ax.xaxis.set_label_position('bottom')
            ax.xaxis.tick_bottom()


   
    if preliminary:
        ax1.set_ylabel('depth [dbar]')
        ax1.set_title('Tempature ' + stationID)

    df.to_csv(plot_path+stationID+'_templog.csv')    
   
    # Show the plot
    fig.savefig(plot_path+stationID+'_templog.png')
    plt.close(fig)
    print('Plot ready')

def plot_taglog(df,stationID, plot_path:str, preliminary=True, depth_min=0,):

    fig, ax1 = plt.subplots(figsize=(10,15))
    fig.subplots_adjust(top=0.97) # Adjust the value as needed
    fig.subplots_adjust(bottom=0.2)

    ax1.invert_yaxis()

    ax2 =ax1.twiny()
    ax3 =ax1.twiny()
    ax4 =ax1.twiny()
    ax5 =ax1.twiny()
    ax6 =ax1.twiny()
   # ax7 =ax1.twiny()

    axes = [ax1,ax2,ax3,ax4,ax5,ax6]
    temp =  ["Lockstate","Amplitude","Frequency","Current","Voltage","pressure [dbar]"]
    Tempr_names = ["Lockstate","Amplitude","Frequency","Current","Voltage"]
    colors = ['red', 'blue', 'lime', 'cyan', 'black']
    positions = [0,40,80,120,160]

    #df.set_index("pressure [dbar]", inplace=True)
    for ax,i,name,color,pos in zip(axes,temp,Tempr_names,colors,positions):
        if i in df.columns:
            ax.plot(df[i], df["pressure [dbar]"] , color=color, label=name)
            ax.set_xlabel(f' {name} ',color=color)
            ax.spines['bottom'].set_color(color)
            ax.tick_params(axis='x', colors=color)
            ax.spines['top'].set_visible(False)
            ax.spines['bottom'].set_position(('outward', pos))
            ax.xaxis.set_label_position('bottom')
            ax.xaxis.tick_bottom()


   
    if preliminary:
        ax1.set_ylabel('depth [dbar]')
        ax1.set_title('Tag-Parameter ' + stationID)
    df.to_csv(plot_path+stationID+'_taglog.csv')
    
    # Show the plot
    fig.savefig(plot_path+stationID+'_taglog.png')
    plt.close(fig)
    print('Plot ready')

def plot_log(imgs_dir,save_dir,log_dir):
    
    taglog_file=''
    loglist=os.listdir(log_dir)
    profile_time_hhmm=int(os.path.basename(imgs_dir)[0:8]+ os.path.basename(imgs_dir)[9:13])
    log_size=0
    for log in loglist:
        if os.path.basename(log)[0:2]=='20' and log.endswith('Templog.txt'):
                
            logtime=int(os.path.basename(log)[0:8]+os.path.basename(log)[9:11]+os.path.basename(log)[13:15])
            if logtime>(profile_time_hhmm-10) and  logtime<(profile_time_hhmm+10):
                if os.stat(os.path.join(log_dir,log)).st_size>log_size:
                    log_size=os.stat(os.path.join(log_dir,log)).st_size
                    templog_file=os.path.join(log_dir,log)
                    
    for log in loglist:
        if os.path.basename(log)[0:2]=='Ta':
                
            logtime=os.path.basename(log).split('_')[1].split('-')[0]+os.path.basename(log).split('_')[1].split('-')[1]+os.path.basename(log).split('_')[1].split('-')[2]
            if logtime==os.path.basename(imgs_dir)[0:8]:
                lfile=os.path.basename(log).replace('T','t')
                taglog_file=os.path.join(log_dir,os.path.join(log,lfile+'.txt'))
                break
    # print("Select Templogfile")
    # templog_file= askopenfilename()
    # print("Select TAGlogfile")
    # taglog_file= askopenfilename()
    #templist=read_templog("D:/templogtest/20240214_01h_34m__Templog.txt")
    [df_templog,station_id,df_timepress]=time_to_press(imgs_dir,templog_file)
    if taglog_file!='':

        df_taglog=read_taglog(df_timepress,taglog_file)
        plot_taglog(df_taglog,station_id, save_dir, preliminary=True, depth_min=0,)
    plot_templog(df_templog,station_id, save_dir, preliminary=True, depth_min=0,)
    