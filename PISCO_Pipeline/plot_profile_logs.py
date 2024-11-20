from Logfile_hist import plot_log
from tkinter.filedialog import askdirectory
import os

LOG_FOLDER="/home/pisco-controller/M202/Logfiles/"
result_folder = "/home/pisco-controller/M202/Log_plots/"
if __name__ == "__main__":
    imgs_dir = askdirectory()    
    save_dir = result_folder+imgs_dir
    os.makedirs(save_dir, exist_ok=True)
    plot_log(imgs_dir,save_dir,LOG_FOLDER)
    print(f'finished plotting logs of {imgs_dir}')