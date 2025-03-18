import os
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('agg')

from pandas.errors import EmptyDataError

import matplotlib.colors as mcolors

#from make_video_from_profile import make_video_pool

IMAGE_SIZE = 2560

VOLUME_PER_IMAGE = 50 * (3.5)**2 * np.pi  # in cubic centimeters
VOLUME_PER_IMAGE_LITERS = VOLUME_PER_IMAGE / 1000  # convert to liters
# esd_bins = np.array([
#                 100.0, 126.0, 158.0, 200.0, 251.0, 316.0, 398.0, 501.0, 631.0, 794.0, 1000.0,
#                 1259.0, 1585.0, 1995.0, 2512.0, 3162.0, 3981.0, 5012.0, 6310.0, 7943.0, 10000.0,
#                 12589.0, 15849.0, 19953.0, 25119.0, 31623.0, 39811.0, 50119.0, 63096.0, 79433.0,
#                 100000.0, 125893.0, 158489.0, 199526.0, 251189.0, 316228.0, 398107.0, 501187.0,
#                 630957.0, 794328.0, 1000000.0, 1258925.0, 1584893.0, 1995262.0, 2511886.0,
#                 3162278.0, 3981072.0, 5011872.0, 6309573.0, 7943282.0, 10000000.0
#             ])
esd_bins = np.array([125,250,500,1000,100000])

depth_bins = 5 #meters

def area_to_esd(area: float) -> float:
    pixel_size = 27 #in µm/pixel @ 2560x2560 
    return 2 * np.sqrt(area * pixel_size**2 / np.pi)

def gen_crop_df(path:str, small:bool):
    '''function that collects all crop information from a given path and puts it in a dataframe. Args: small: if set to True all particle objects from the segmentation will be listed in the df or else only the ones that were saved as crops.'''
    
    print('... calculating crop dataframe.')
    files = [os.path.join(path, file) for file in sorted(os.listdir(path)) if file.endswith(".csv")]
    dataframes = []
    empty_file_counter = 0
    id = 1
    for file in files:
        if 'settings' in file:
            continue
        #print(file)
        try:
            df = pd.read_csv(file, delimiter=",", header=None)
            df.insert(0,'',id)
            dataframes.append(df)
            id+=1
        except EmptyDataError:
            empty_file_counter += 1
            print(f"File {file} is empty")
    df = pd.concat(dataframes, ignore_index=True)
    headers = ["img_id","index", "filename", "mean_raw", "std_raw", "mean_corr", "std_corr", "area", "x", "y", "w", "h", "saved"]
    df.columns = headers
    df.reset_index(drop=True, inplace=True)
    df.drop("index", axis=1, inplace=True)

    if not small:
        df = df[df["saved"] == 1]
    #df.drop("saved", axis=1, inplace=True)

    # Split the 'filename' column
    split_df = df['filename'].str.split('_', expand=True)
    headers = ["cruise","dship_id","camera","meta", "date-time","index"]
    split_df.columns = headers
    meta_df = split_df['meta'].str.split('-', expand=True)
    meta_headers = ["pressure","Lat","Lon","temperature"]
    meta_df.columns = meta_headers
    #split_df.drop("x", axis=1, inplace=True)
    split_df=pd.concat([split_df, meta_df], axis=1)
    split_df['pressure'] = split_df['pressure'].str.replace('dbar', '').astype(float)
    split_df['temperature'] = split_df['temperature'].str.replace('C', '').astype(float)
    split_df['index'] = split_df['index'].str.replace('.jpg', '').astype(int)

    # Concatenate the new columns with the original DataFrame
    df = pd.concat([split_df, df], axis=1)

    # Drop the original 'filename' column
    df = df.drop('filename', axis=1)
    df = df.drop('meta', axis=1)

    df['esd'] = df['area'].apply(area_to_esd).round(2)
    #df['pressure'] = (df['pressure']-1)*10
    df.rename(columns={'pressure': 'pressure [dbar]'}, inplace=True)

    # Sort the DataFrame by the 'date-time' column
    df = df.sort_values(by='date-time', ascending=True)
    df.reset_index(drop=True, inplace=True)

    return df

def add_ctd_data(ctd_data_loc:str, crop_df):
    '''function that adds the ctd data from a given location to the crop dataframe '''

    # Reading the specified header line (line 124) to extract column names
    with open(ctd_data_loc, 'r') as file:
        for _ in range(123):
            next(file)  # Skip lines until the header
        header_line = next(file).strip()  # Read the header line

    # Processing the header line to get column names
    # The header line is expected to be in the format "Columns  = column1:column2:..."
    column_names = header_line.split(' = ')[1].split(':')
    ctd_df = pd.read_csv(ctd_data_loc, delim_whitespace=True, header=None, skiprows=124, names=column_names)
    ctd_df['z_factor']=ctd_df['z']/ctd_df['p']
    
    # Function to interpolate a column based on closest pressure values
    def interpolate_column(pressure, column):
        # Sort 'p' values based on the distance from the current pressure
        closest_ps = ctd_df['p'].iloc[(ctd_df['p'] - pressure).abs().argsort()[:2]]
        
        # Get corresponding column values
        column_values = ctd_df.loc[closest_ps.index, column]
        
        # Linear interpolation
        return np.interp(pressure, closest_ps, column_values)
    
    # Columns to interpolate
    columns = ['s', 'o', 't', 'chl', 'z_factor']

    # Identify unique pressures and calculate their interpolated 's' values
    unique_pressures = crop_df['pressure [dbar]'].unique()

    # Interpolate for each column and store the results in a dictionary
    interpolated_columns = {column: {pressure: interpolate_column(pressure, column) 
                                    for pressure in unique_pressures}
                            for column in columns}

    for column in columns:
        new_col_name = f'interpolated_{column}'
        crop_df[new_col_name] = crop_df['pressure [dbar]'].map(interpolated_columns[column])
    # Determine the position of pressure column
    position = crop_df.columns.get_loc('pressure [dbar]') + 1

    # Insert a new column. For example, let's insert a column named 'new_column' with a constant value
    crop_df.insert(position, 'depth [m]', (crop_df['pressure [dbar]']*crop_df['interpolated_z_factor']).round(3))

    return crop_df

def generate_video():
    '''function to create a video of the whole dataset for better overview.'''



def check_log():
    '''function to check if there a TAG Lens relocks (or hardware temperature excursions) that potentially render the image information corrupt.'''


def check_ctd_data(): 
    '''function to check for strong gradients in CTD data that indicate jumps in water charcteristics that potentially lead to schlieren in images.'''

def calculate_object_properties():
    '''Inspired from morphocut, based on sklearn.measure.regionprops()'''

def plot_histogram(df, plot_path:str):
    log_bins = np.logspace(np.log10(df["esd"].min()), np.log10(df["esd"].max()), num=500)
    #print(len(df.index))
    plt.hist(df["esd"], bins=log_bins, log=True)
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("ESD")
    plt.ylabel("Frequency")
    plt.title("Histrogram of esds")
    plt.savefig(plot_path+'_esd_hist.png')

def populate_esd_bins(df, esd_bins=np.array([125,250,500,1000,100000]), depth_bin_size=5):

    # Define depth bins with an interval of 5 m
    max_depth = df['depth [m]'].max()
    min_depth = df['depth [m]'].min()
    depth_bins = np.arange(min_depth, max_depth + depth_bin_size, depth_bin_size)

    # Assign each 'esd' and 'depth [m]' value to its respective bin
    df['esd_bin'] = np.digitize(df['esd'], esd_bins)
    df['depth_bin'] = np.digitize(df['depth [m]'], depth_bins)

    # Group by the depth bin and count unique values in 'depth [m]'
    depth_bin_volumes = df.groupby('depth_bin')['img_id'].nunique()*VOLUME_PER_IMAGE_LITERS

    # Group by 'esd_bin' and 'depth_bin' and count occurrences
    histogram = df.groupby(['esd_bin', 'depth_bin']).size().reset_index(name='count')
    histogram['normalized_count'] = histogram.apply(lambda row: row['count'] / depth_bin_volumes.get(row['depth_bin'], 1), axis=1)

    # Get histogram with exact depth (more finegrained)
    #histogram2 = df.groupby(['img_id','esd_bin','depth [m]' ]).size().reset_index(name='count')
    #histogram2['normalized_count'] = histogram2.apply(lambda row: row['count'] / VOLUME_PER_IMAGE_LITERS, axis=1)
    
    # Pivot the dataframe to make 'esd_bin' values as column headers
    pivoted_df = histogram.pivot(index='depth_bin', columns='esd_bin', values='normalized_count').reset_index()
    #pivoted_df2 = histogram2.pivot(index='img_id', columns='esd_bin', values='normalized_count').reset_index()

    # Rename columns for clarity
    pivoted_df.columns = ['depth [m]', 'ESD<125um', 'ESD 125-250um', 'ESD 250-500um', 'ESD 500-1000um', 'ESD >1000um']
    #pivoted_df2.columns = ['depth_bin', 'ESD<125um', 'ESD 125-250um', 'ESD 250-500um', 'ESD 500-1000um', 'ESD >1000um']

    return histogram, pivoted_df

def populate_esd_bins_pressure(df,  depth_bin_size, esd_bins=np.array([0,125,250,500,1000,100000])):

    # Define depth bins with an interval of 5 m
    max_depth = df['pressure [dbar]'].max()
    min_depth = df['pressure [dbar]'].min()
    depth_bins = np.arange(min_depth, max_depth + depth_bin_size, depth_bin_size)

    # Assign each 'esd' and 'depth [m]' value to its respective bin
    df['esd_bin'] = np.digitize(df['esd'], esd_bins)
    df['depth_bin'] = np.digitize(df['pressure [dbar]'], depth_bins)

    # Group by the depth bin and count unique values in 'depth [m]'
    depth_bin_volumes = df.groupby('depth_bin')['img_id'].nunique()*VOLUME_PER_IMAGE_LITERS

    # Group by 'esd_bin' and 'depth_bin' and count occurrences
    histogram = df.groupby(['esd_bin', 'depth_bin']).size().reset_index(name='count')
    histogram['normalized_count'] = histogram.apply(lambda row: row['count'] / depth_bin_volumes.get(row['depth_bin'], 1), axis=1)

    # Get histogram with exact depth (more finegrained)
    #histogram2 = df.groupby(['img_id','esd_bin','depth [m]' ]).size().reset_index(name='count')
    #histogram2['normalized_count'] = histogram2.apply(lambda row: row['count'] / VOLUME_PER_IMAGE_LITERS, axis=1)
    
    # Pivot the dataframe to make 'esd_bin' values as column headers
    pivoted_df = histogram.pivot(index='depth_bin', columns='esd_bin', values='normalized_count').reset_index()
    #pivoted_df2 = histogram2.pivot(index='img_id', columns='esd_bin', values='normalized_count').reset_index()

    # Rename columns for clarity
    #pivoted_df.columns = ['depth_bin', 'ESD<125um', 'ESD 125-250um', 'ESD 250-500um', 'ESD 500-1000um', 'ESD >1000um']
    #pivoted_df2.columns = ['depth_bin', 'ESD<125um', 'ESD 125-250um', 'ESD 250-500um', 'ESD 500-1000um', 'ESD >1000um']

    return histogram, pivoted_df

def plot_particle_dist(grouped, stationID:str, plot_path:str, depth_bin_size=5, preliminary=True, depth_min=0):

    fig, ax1 = plt.subplots(figsize=(10,15))
    fig.subplots_adjust(top=0.97) # Adjust the value as needed
    fig.subplots_adjust(bottom=0.2)

    ax1.invert_yaxis()

    ax2 =ax1.twiny()
    ax3 =ax1.twiny()
    ax4 =ax1.twiny()
    ax5 =ax1.twiny()

    axes = [ax1,ax2,ax3,ax4,ax5]
    esd_bins = [1,2,3,4,5]
    esd_bin_names = ['<125um','125-250um','250-500um','500-1000um','>1000um']
    colors = ['red', 'blue', 'lime', 'cyan', 'black']
    positions = [0,40,80,120,160]


    for ax,i,name,color,pos in zip(axes,esd_bins,esd_bin_names,colors,positions):
        if i in grouped.columns:
            ax.plot(grouped[i], grouped['depth_bin']*depth_bin_size+depth_min, color=color, label=name)
            ax.set_xlabel(f'normalized abundance LPM {name} [#/L]',color=color)
            ax.spines['bottom'].set_color(color)
            ax.tick_params(axis='x', colors=color)
            ax.spines['top'].set_visible(False)
            ax.spines['bottom'].set_position(('outward', pos))
            ax.xaxis.set_label_position('bottom')
            ax.xaxis.tick_bottom()


    # ax2.set_xlabel('normalized abundance LPM ESD 125-250um [#/L]',color='blue')
    # ax2.spines['top'].set_visible(False)
    # ax2.spines['bottom'].set_position(('outward', 40))
    # ax2.spines['bottom'].set_color('blue')
    # ax2.xaxis.set_label_position('bottom')
    # ax2.xaxis.tick_bottom()
    # ax2.tick_params(axis='x', colors='blue')
    # ax2.plot(grouped[2], grouped['depth_bin']*depth_bin_size+depth_min, color='blue', label='LPM 125-250um')

    # ax3.spines['top'].set_visible(False)
    # ax3.spines['bottom'].set_position(('outward', 80))
    # ax3.spines['bottom'].set_color('lime')
    # ax3.xaxis.set_label_position('bottom')
    # ax3.xaxis.tick_bottom()
    # ax3.set_xlabel('normalized abundance LPM ESD 250-500um [#/L]',color='lime')
    # ax3.tick_params(axis='x', colors='lime')
    # ax3.plot(grouped[3], grouped['depth_bin']*depth_bin_size+depth_min, color='lime', label='LPM 250-500um')

    # ax4.spines['top'].set_visible(False)
    # ax4.spines['bottom'].set_position(('outward', 120))
    # ax4.spines['bottom'].set_color('cyan')
    # ax4.xaxis.set_label_position('bottom')
    # ax4.xaxis.tick_bottom()
    # ax4.set_xlabel('normalized abundance LPM ESD 500-1000um [#/L]',color='cyan')
    # ax4.tick_params(axis='x', colors='cyan')
    # ax4.plot(grouped[4], grouped['depth_bin']*depth_bin_size+depth_min, color='cyan', label='LPM 500-1000um')
 
    # ax5.spines['top'].set_visible(False)
    # ax5.spines['bottom'].set_position(('outward', 160))
    # ax5.spines['bottom'].set_color('black')
    # ax5.xaxis.set_label_position('bottom')
    # ax5.xaxis.tick_bottom()
    # ax5.set_xlabel('normalized abundance LPM ESD >1000um [#/L]',color='black')
    # ax5.tick_params(axis='x', colors='black')
    # ax5.plot(grouped[5], grouped['depth_bin']*depth_bin_size+depth_min, color='black', label='LPM >1000um')

    # Set the labels and legend
    #plt.xlabel('LPM Abundance')
    if preliminary:
        ax1.set_ylabel('binned depth [dbar]')
        ax1.set_title('Preliminary PIScO LPM Distribution ' + stationID)
    else:
        ax1.set_ylabel('binned depth [m]')
        ax1.set_title('LPM Distribution')
    #ax1.legend(loc='best')

    # Show the plot
    fig.savefig(plot_path+'_particle_dist.png')
    plt.close(fig)

def plot_position_hist(df,plot_path):
    plt.subplot(121)
    plt.hist(df["x"], bins=100)
    plt.xlim([0, IMAGE_SIZE])
    plt.xlabel("x-positions")
    plt.ylabel("Frequency")
    plt.title("Histrogram of \n x-positions")
    plt.subplot(122)
    plt.hist(df["y"], bins=100)
    plt.xlim([0, IMAGE_SIZE])
    plt.xlabel("y-positions")
    plt.title("Histrogram of \n y-positions")
    plt.savefig(plot_path+'_position_hist.png')
    plt.close()

def plot_2d_histogram(df,plot_path):
    hist2d = plt.hist2d(df["x"], df["y"], bins=np.linspace(0, IMAGE_SIZE-1, 500), norm=mcolors.PowerNorm(0.5))
    plt.colorbar()
    gca = plt.gca()
    gca.invert_xaxis()
    gca.invert_yaxis()
    plt.xlabel("x-position")
    plt.ylabel("y-position")
    plt.title("2D Histogram of object positions")
    plt.savefig(plot_path +'_2d_hist.png')
    plt.close()

def add_hist_value(df):
    def computeHist(x, y, nBins):
        step = IMAGE_SIZE / nBins
        hist = [[0 for j in range(nBins)] for i in range(nBins)]
        hist = np.zeros((nBins, nBins),dtype=np.int64)
        for row in range(len(x)):
            try:
                x_index = int(x[row] // step)
                y_index = int(y[row] // step)
                hist[y_index, x_index] += 1
            except:
                pass
        return hist
    
    hist = computeHist(df["x"], df["y"], 500)

    def get_hist_value(x, y):
        step = 2560 / 500
        x_index = int(x // step )
        y_index = int(y // step )
        return hist[x_index][y_index]
    
    df["position_hist_value"] = df.apply(lambda row: get_hist_value(row["x"], row["y"]), axis=1)

    return df

def plot_means(df, plot_path):
    x_values_raw = df['mean_raw']
    y_values = df['pressure [dbar]']
    std_values_raw = df['std_raw']
    x_values_corr = df['mean_corr']
    std_values_corr = df['std_corr']

    x_raw_left = x_values_raw - std_values_raw
    x_raw_right = x_values_raw + std_values_raw
    x_corr_left = x_values_corr - std_values_corr
    x_corr_right = x_values_corr + std_values_corr

    fig, ax = plt.subplots(figsize=(10,15))

    ax.invert_yaxis()
    ax.plot(x_values_raw, y_values, label='mean raw')
    ax.fill_betweenx(y_values, x_raw_left, x_raw_right, color='gray', alpha=0.5, label='±1 STD')
    ax.plot(x_values_corr, y_values, label='mean corr')
    ax.fill_betweenx(y_values, x_corr_left, x_corr_right, color='gray', alpha=0.5, label='±1 STD')
    ax.set_ylabel('raw pressure [dbar]')
    ax.set_xlabel('image grey level')

    ax.legend()

    fig.savefig(plot_path +'_img_means.png')
    plt.close(fig)
    




