# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
from dash import dcc
from dash import html
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, Input, Output, callback, dash_table, State
import dash_bootstrap_components as dbc

import os
import numpy as np
import pandas as pd

from pandas.errors import EmptyDataError

from sqlalchemy import create_engine
from sqlalchemy import text

from PIL import Image
import time
import pickle
#import h5py
#import umap

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.state_variable = None

#Server-side variables
original_df = None
original_pivoted_df = None
global_unique_df = None

original_ctd_fig = None
original_particles_fig = None
original_tag_t_fig = None

original_features_fig = None
loaded__embedding = None
loaded_normal_embedding = None
temp_features_fig = None
loaded_obj_ids = None

#video_src = None

### fixed variables
VOLUME_PER_IMAGE = 50 * (3.5)**2 * np.pi  # in cubic centimeters
VOLUME_PER_IMAGE_LITERS = VOLUME_PER_IMAGE / 1000  # convert to liters
IMAGE_SIZE = 2560
depth_bin_size = 1

### Setup SQL Database
#Setup connection parameters
username = 'plankton'
password = 'piscodisco'
host = 'localhost'  # or the IP address of your database server
port = '5432'       # default port for PostgreSQL
database = 'pisco_crops_db'

# Create an engine that connects to the PostgreSQL server
engine = create_engine(f'postgresql://{username}:{password}@{host}:{port}/{database}')

# Fetch all table names in the database
query_tables = "SELECT tablename FROM pg_tables WHERE schemaname='public'"
with engine.connect() as conn:
    table_names = pd.read_sql_query(text(query_tables), conn)['tablename'].tolist()

table_names = sorted(table_names)

# query = f'SELECT * FROM "M181-126-1_CTD-040_00deg00S-010deg00W_20220505-1401"'
# df = pd.read_sql_query(query, engine)
# df_unique = df[['date-time', 'pressure [dbar]', 'depth [m]', 'img_id','temperature','overview_path','interpolated_s','interpolated_t','interpolated_o','interpolated_chl','interpolated_z_factor']].drop_duplicates()
# #df_unique = df[['date-time']].drop_duplicates()
# df_count = df.groupby('date-time').size().reset_index(name='count')
# df_unique = df_unique.merge(df_count, on='date-time', how='left')
# df_unique = df_unique.sort_values('pressure [dbar]')

# def load_features(file):
#     with h5py.File(file, 'r') as f:
#         data = {key: value[:] for key, value in f.items()}
#     return data

### Functions for data analysis and plotting
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
    
    # Pivot the dataframe to make 'esd_bin' values as column headers
    pivoted_df = histogram.pivot(index='depth_bin', columns='esd_bin', values='normalized_count').reset_index()

    return histogram, pivoted_df

def plot_ctd_data(df, maximum_y_value=None, selected_pressure=None):
    # Create a layout with 2 x-axis
    layout = go.Layout(
        xaxis=dict(
            title='interpolated_s',
            color='red'
        ),
        xaxis2=dict(
            title='interpolated_t',
            color='blue',
            overlaying='x',
            side='top'
        ),
        xaxis3=dict(
            title='interpolated_o',
            color='lime',
            overlaying='x',
            side='bottom',
            position=0.85 # controls the vertical position of the axis
        ),
        xaxis4=dict(
            title='interpolated_chl',
            color='cyan',
            overlaying='x',
            side='top',
            position=0.90 # controls the vertical position of the axis
        ),
        xaxis5=dict(
            title='interpolated_z_factor',
            color='black',
            overlaying='x',
            side='bottom',
            position=0.95 # controls the vertical position of the axis
        ),
        yaxis=dict(
            title='depth [dbar]',
            #range=[df['pressure [dbar]'].min(), df['pressure [dbar]'].max()],
            #autorange=False,
            autorange='reversed', # this line achieves the 'ax1.invert_yaxis()' functionality
        ),
        autosize=False,
        width=500,
        height=900,
        #title='Preliminary CTD data ' 
    )  

    # # Add your data to the plot
    if selected_pressure is not None:
        # Add a horizontal line at the selected pressure
        fig = go.Figure(data=[
            go.Scatter(x=df['interpolated_s'], y=df['pressure [dbar]'], name='salinity', xaxis='x', yaxis='y', line=dict(color='red')),
            go.Scatter(x=df['interpolated_t'], y=df['pressure [dbar]'], name='temperature', xaxis='x2', yaxis='y', line=dict(color='blue')),
            go.Scatter(x=df['interpolated_o'], y=df['pressure [dbar]'], name='oxygen', xaxis='x3', yaxis='y', line=dict(color='lime')),
            go.Scatter(x=df['interpolated_chl'], y=df['pressure [dbar]'], name='chl', xaxis='x4', yaxis='y', line=dict(color='cyan')),
            #go.Scatter(x=df['interpolated_z_factor'], y=df['pressure [dbar]'], name='interpolated_z_factor', xaxis='x5', yaxis='y', line=dict(color='black')),
            
        ], layout=layout,)
        fig.add_hline(y=selected_pressure, line_width=3, line_dash="dash", line_color="red")

    if selected_pressure is None:
        fig = go.Figure(data=[
            go.Scatter(x=df['interpolated_s'], y=df['pressure [dbar]'], name='salinity', xaxis='x', yaxis='y', line=dict(color='red')),
            go.Scatter(x=df['interpolated_t'], y=df['pressure [dbar]'], name='temperature', xaxis='x2', yaxis='y', line=dict(color='blue')),
            go.Scatter(x=df['interpolated_o'], y=df['pressure [dbar]'], name='oxygen', xaxis='x3', yaxis='y', line=dict(color='lime')),
            go.Scatter(x=df['interpolated_chl'], y=df['pressure [dbar]'], name='chl', xaxis='x4', yaxis='y', line=dict(color='cyan')),
            #go.Scatter(x=df['interpolated_z_factor'], y=df['pressure [dbar]'], name='interpolated_z_factor', xaxis='x5', yaxis='y', line=dict(color='black')),
        ],layout=layout)
    
     # Get the first and last occurrence of each unique value in 'TAG_event' that is larger than 0
    unique_values = df['TAG_event'].unique()  

    for value in unique_values:
        if value > 0:
            occurrences = df[df['TAG_event'] == value]
            first_occurrence = occurrences.iloc[0]
            last_occurrence = occurrences.iloc[-1]
            fig.add_hrect(
                    y0=first_occurrence['pressure [dbar]']-4,
                    y1=last_occurrence['pressure [dbar]']+4,
                    fillcolor="LightSkyBlue",
                    opacity=0.25,
                )
    
    # Identify ranges where 'part_based_filter' is 1
    ranges = df[df['part_based_filter'].diff() != 0]

    # Iterate over ranges
    for i in range(0, len(ranges)-1, 2):  # step by 2 to get start and end of each range
        start = ranges.iloc[i]  # Start of range where 'part_based_filter' is 1
        end = ranges.iloc[i+1]  # End of range where 'part_based_filter' changes to 0
        fig.add_hrect(y0=start['pressure [dbar]'], y1=end['pressure [dbar]'], fillcolor="LightGreen", opacity=0.25)
    fig.update_xaxes(fixedrange=True)    
    return fig

def plot_particles_distribution(grouped, depth_min=0, depth_bin_size=1, selected_pressure=None):
    fig = go.Figure()

    esd_bins = [1,2,3,4,5]
    esd_bin_names = ['<125um','125-250um','250-500um','500-1000um','>1000um']
    colors = ['red', 'blue', 'lime', 'cyan', 'black']

    for i, name, color in zip(esd_bins, esd_bin_names, colors):
        if i in grouped.columns:
            fig.add_trace(go.Scatter(x=grouped[i],
                                    y=grouped['depth_bin']*depth_bin_size+depth_min,
                                    mode='lines',
                                    name=name,
                                    line=dict(color=color)))
    if selected_pressure is not None:
        fig.add_hline(y=selected_pressure, line_width=3, line_dash="dash", line_color="red")

    fig.update_layout(#title='PIScO LPM Distribution ',
                    xaxis_title='LPM Abundance',
                    yaxis_title='binned depth [dbar]',
                    yaxis={'autorange': 'reversed'},
                    autosize=False,
                    width=500,
                    height=900,
                )
    #fig.update_xaxes(fixedrange=True)
    return fig

def plot_tag_temperatures(df, depth_min=0, selected_pressure=None):
    fig = go.Figure()

    keys = ['TT','T1','T2','TH']
    colors = ['red', 'blue', 'lime', 'cyan']

    for key, color in zip(keys, colors):
        if key in df.columns:
            fig.add_trace(go.Scatter(x=df[key],
                                    y=df['pressure [dbar]'],
                                    mode='lines',
                                    name=key,
                                    line=dict(color=color)))
    if selected_pressure is not None:
        fig.add_hline(y=selected_pressure, line_width=3, line_dash="dash", line_color="red")

    fig.update_layout(#title='PIScO TAG Temperatures ',
                    xaxis_title='T [°C]',
                    yaxis_title='pressure [dbar]',
                    yaxis={'autorange': 'reversed'},
                    autosize=False,
                    width=500,
                    height=900,
                )
    #fig.update_xaxes(fixedrange=True)
    return fig

def plot_features(embedding, object_ids):  
    fig = go.Figure()
    fig.add_trace(px.scatter(x=embedding[:, 0],
                            y=embedding[:, 1],
                            #mode='markers',
                            hover_name=object_ids,
                            #marker=dict(color='blue'),
                            render_mode='svg',
                            )
                    )
    fig.update_layout(xaxis_title='X', yaxis_title='Y')
   

#### LAYOUT ####

# Use the function as the figure in a dcc.Graph component
app.layout = dbc.Container([
    html.P("Select profile"),
    dcc.Loading(
            id="loading",
            type="circle",
            children=[
                dcc.Dropdown(table_names, placeholder="Select a profile", id='dropdown'),
            ],
        ),
    dbc.Alert(id='msg'),
    dbc.Row([
        dbc.Col([
            dcc.Tabs([
                dcc.Tab(
                    label='CTD', children=[
                    dcc.Graph(id='ctd',figure={}), 
                    ]),
                dcc.Tab(
                    label='TAG_Temp', children=[
                    dcc.Graph(id='tag_t',figure={}), 
                    ]),
                ]),
            ], width=4),
        dbc.Col([
            dcc.Tabs([
                dcc.Tab(
                    label='Particles', children=[
                    dcc.Graph(id='particles',figure={}),
                    ]),
                dcc.Tab(
                    label='TAG_Log', children=[
                    dcc.Graph(id='tag_log',figure={}), 
                    ]),
                ]),
            ], width=4),
        dbc.Col([
            dcc.Tabs([
                dcc.Tab(
                    label='Full frame', children=[
                    dcc.Graph(id='img', figure={'data': [], 'layout': {'width': 500, 'height': 500}}),
                    ]),
                dcc.Tab(
                    label='raw', children=[
                    dcc.Graph(id='raw', figure={}),
                    ]),
                dcc.Tab(
                    label='Profile Video', children=[
                    html.Video(id='video', src='', controls=True, style={'width': '75%','height': '40vh','position': 'relative', 'left': '50px', 'top': '50px'}),
                    ]),
                ]),
            dcc.Graph(id='crop', figure={'data': [], 'layout': {'width': 500, 'height': 500}}),
        ], width=4, )  
    ]),
    dcc.Graph(id='features',figure={'data': [], 'layout': {'width': 800, 'height': 800}}),
    dcc.Store(id='df'),
    dcc.Store(id='pivoted_df'),
    dbc.Label('List of crops in selected image:'),
    dash_table.DataTable(
        data=[],
        #columns={},#[{"name": i, "id": i} for i in df.columns],
        id='tbl_crops', 
        row_selectable='single',
        page_action='native',
        page_current= 0,
        page_size= 20,
        virtualization=True,
        #filter_action='native',
    ),
    dbc.Label('Image selection:'),
    dash_table.DataTable(
        data=[], #df_unique.to_dict('records'),
        #columns={},#[{"name": i, "id": i} for i in df_unique.columns],
        id='tbl', 
        row_selectable='single',
        page_action='native',
        page_current= 0,
        page_size= 20,
        virtualization=True,
        #filter_action='native',
    ),
    
    #dbc.Alert(id='tbl_crops'),
    dcc.Store(id='stored-pressure'),
])

#### CALLBACKS ####

#dropdown callback
@app.callback(
    [Output('tbl','data', allow_duplicate=True),
     Output('tbl','columns', allow_duplicate=True), 
     Output('df', 'data'),
     Output('msg', 'children', allow_duplicate=True),
     Output('ctd', 'figure', allow_duplicate=True),
     Output('particles', 'figure', allow_duplicate=True),
     Output('tag_t', 'figure', allow_duplicate=True),
     Output('pivoted_df', 'data'),
     Output('video', 'src'),
     Output('features', 'figure', allow_duplicate=True)],
    [Input('dropdown', 'value')],
    prevent_initial_call=True
)
def update_on_dropdown(profile):
    if profile:
        global original_ctd_fig
        global original_particles_fig
        global original_df
        global original_pivoted_df
        global loaded_relock_embedding
        global loaded_normal_embedding
        global temp_features_fig
        global original_features_fig
        global global_unique_df
        global loaded_obj_ids
        
        print('starting...')
        root='/media/plankton/30781fe1-cea5-4503-ae00-1986beb935d2/Segmentation_results/M181/results_240328'

        query = f'SELECT * FROM "{profile}"'
        df = pd.read_sql_query(query, engine)            
        df_unique = df[['date-time', 'pressure [dbar]', 'depth [m]', 'img_id','temperature','overview_path','interpolated_s','interpolated_t','interpolated_o','interpolated_chl','interpolated_z_factor','relock','restart','TT','T1','T2','TH','TAG_event','part_based_filter']].drop_duplicates()
        df_count = df.groupby('date-time').size().reset_index(name='count')
        df_unique = df_unique.merge(df_count, on='date-time', how='left')
        df_unique = df_unique.sort_values('pressure [dbar]')
        global_unique_df = df_unique
        columns = [{"name": i, "id": i} for i in df_unique.columns]
        print('df read...')
        #print('df_unique length:',df_unique.head())

        _, pivoted_df = populate_esd_bins_pressure(df, depth_bin_size=depth_bin_size, esd_bins=np.array([0,125,250,500,1000,100000]))
        #store the original dfs
        original_df = df
        original_pivoted_df = pivoted_df
        print('df pivoted...')

        # Update graph
        graph_fig = plot_ctd_data(df_unique)
        part_fig = plot_particles_distribution(grouped=pivoted_df)
        tag_t_fig = plot_tag_temperatures(df_unique)

        #store the original figures
        original_ctd_fig = graph_fig
        original_particles_fig = part_fig
        original_tag_t_fig = tag_t_fig
        print('plots drawn...')

        #store the video src
        video_src = os.path.dirname(os.path.dirname(df['overview_path'].iloc[0])) + '/segmented_profile_video.mp4'
        print(video_src)

        #plot the featues
        #features_loc = os.path.dirname(os.path.dirname(df['overview_path'].iloc[0])) + '/handcrafted_embedding.pkl'
        # features_dict = load_features(features_loc)

        df_relock = df[df['TAG_event'] != 0]
        df_normal = df[df['TAG_event'] == 0]

        relock_object_ids = df_relock['obj_id'].tolist()
        normal_object_ids = df_normal['obj_id'].tolist()

        relock_embedding = np.array(list(zip(df_relock['umap_x'], df_relock['umap_y'])))
        normal_embedding = np.array(list(zip(df_normal['umap_x'], df_normal['umap_y'])))

        #object_ids = relock_object_ids + normal_object_ids

        loaded_relock_embedding= relock_embedding
        loaded_normal_embedding = normal_embedding
        loaded_obj_ids = normal_object_ids

        #print(len(object_ids), len(embedding))
        #features_fig = plot_features(embedding, object_ids)
        features_fig = px.scatter(x=relock_embedding[:, 0],
                            y=relock_embedding[:, 1],
                            #mode='markers',
                            hover_name=relock_object_ids,
                            color_discrete_sequence=['black'],
                            render_mode='svg',
                            )
        features_fig.add_trace(px.scatter(x=normal_embedding[:, 0],
                            y=normal_embedding[:, 1],
                            #mode='markers',
                            hover_name=normal_object_ids,
                            color_discrete_sequence=['blue'],
                            render_mode='svg',
                            ).data[0])
        original_features_fig = features_fig
        temp_features_fig = features_fig

        return df_unique.to_dict('records'), columns, df.to_dict('records'), f"{profile} selected", graph_fig, part_fig, tag_t_fig, pivoted_df.to_dict('records'), video_src, features_fig
    else:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, go.Figure(), go.Figure(), go.Figure(), dash.no_update, dash.no_update, go.Figure()

#figures callback
@app.callback(
    [Output('ctd', 'figure', allow_duplicate=True),
     Output('img', 'figure', allow_duplicate=True),
     Output('particles', 'figure', allow_duplicate=True),
     Output('tag_t', 'figure', allow_duplicate=True),
     Output('features', 'figure', allow_duplicate=True),
     Output('stored-pressure', 'data', allow_duplicate=True),
     Output('tbl_crops', 'data', allow_duplicate=True),
     Output('tbl_crops', 'columns', allow_duplicate=True),
     Output('msg', 'children', allow_duplicate=True),
     Output('tbl', 'selected_rows', allow_duplicate=True),
     Output('tbl', 'page_current')
     ],
    [Input('tbl', 'selected_rows'),
     Input('particles', 'relayoutData'),
     Input('ctd', 'relayoutData'),
     Input('ctd', 'clickData'),
     ],
     [State('ctd', 'figure'),  # get the current state of ctd figure
     State('particles', 'figure'),
     State('tag_t', 'figure'),
     ],
    prevent_initial_call=True
)
def update_figures(selected_rows, particles_relayout_data, ctd_relayout_data, ctd_click, ctd_fig, particles_fig, tag_t_fig):
    global original_ctd_fig
    global original_particles_fig
    global original_df
    global original_features_fig
    global temp_features_fig
    global loaded_embedding
    global global_unique_df

    ctx = dash.callback_context

    if not ctx.triggered:
        return dash.no_update
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'tbl':
        if selected_rows:

            selected_row = original_df.iloc[selected_rows[0]]
            selected_pressure = selected_row['pressure [dbar]']
            selected_datetime = selected_row['date-time']  

            # Update image
            image_name = selected_row['overview_path']
            img = Image.open(image_name)
            upd_img_fig = px.imshow(img, title=os.path.basename(image_name))

        # Update graph
            #_, pivoted_df = populate_esd_bins_pressure(full_df, depth_bin_size=depth_bin_size, esd_bins=np.array([0,125,250,500,1000,100000]))
            #pivoted_df = pd.DataFrame.from_dict(pivoted_df)
            #upd_ctd_fig = plot_ctd_data(pd.DataFrame(data), selected_pressure=selected_pressure)
            #upd_particles_fig = plot_particles_distribution(grouped=pivoted_df, selected_pressure=selected_pressure)
            ctd_fig = go.Figure(original_ctd_fig)
            particles_fig = go.Figure(original_particles_fig)
            tag_t_fig = go.Figure(original_tag_t_fig)

            # Add horizontal line to figures
            ctd_fig.add_hline(y=selected_pressure, line_width=3, line_dash="dash", line_color="red")
            particles_fig.add_hline(y=selected_pressure, line_width=3, line_dash="dash", line_color="red")
            tag_t_fig.add_hline(y=selected_pressure, line_width=3, line_dash="dash", line_color="red")

            # Convert figures back to dictionaries
            upd_ctd_fig = ctd_fig.to_dict()
            upd_particles_fig = particles_fig.to_dict()
            upd_tag_t_fig = tag_t_fig.to_dict()

            # Filter the DataFrame based on the selected date-time
            #full_df = pd.DataFrame.from_dict(full_df)
            full_df = original_df
            filtered_df = full_df[full_df['date-time'] == selected_datetime]
            columns = [{"name": i, "id": i} for i in filtered_df.columns]

            return upd_ctd_fig, upd_img_fig, upd_particles_fig, upd_tag_t_fig, dash.no_update, selected_pressure, filtered_df.to_dict('records'), columns, f"{selected_datetime} selected", dash.no_update, dash.no_update

    elif button_id == 'particles':
        if particles_relayout_data is not None and 'yaxis.range[0]' in particles_relayout_data and 'yaxis.range[1]' in particles_relayout_data:
            y_range = [particles_relayout_data['yaxis.range[0]'], particles_relayout_data['yaxis.range[1]']]

            ctd_fig = go.Figure(ctd_fig)
            ctd_fig.update_yaxes(range=y_range, autorange=False)
            ctd_fig_dict = ctd_fig.to_dict()

            tag_t_fig = go.Figure(tag_t_fig)
            tag_t_fig.update_yaxes(range=y_range, autorange=False)
            tag_t_fig_dict = tag_t_fig.to_dict()

            return ctd_fig_dict, dash.no_update, dash.no_update, tag_t_fig_dict, dash.no_update, dash.no_update, dash.no_update, dash.no_update, f"zoomed to {y_range} ", dash.no_update, dash.no_update

    elif button_id == 'ctd':
    
        if ctd_click is not None:
            print(ctd_click)
            start_time = time.time()
            y_coord = ctd_click['points'][0]['y']
            updated_pressure = y_coord
            # Update image
            data_df = original_df#pd.DataFrame(data)
            index = data_df[data_df['pressure [dbar]']==y_coord].index[0]
            selected_row = data_df.iloc[index]
            image_name = selected_row['overview_path']
            img = Image.open(image_name)
            updated_img_fig = px.imshow(img, title=os.path.basename(image_name))
            end_time1 = time.time()
            time1 = end_time1 - start_time

            # Filter the DataFrame based on the selected date-time
            selected_datetime = selected_row['date-time']
            #full_df = pd.DataFrame.from_dict(full_df)
            #full_df = original_df
            #highlight selected row in data tbl
            #unique_df = pd.DataFrame.from_dict(tbl_data)
            idx_unique_df = global_unique_df[global_unique_df['date-time'] == selected_datetime].index[0]
            page_number = idx_unique_df // 20 if idx_unique_df else 0

            filtered_df = data_df[data_df['date-time'] == selected_datetime]
            columns = [{'name': i, 'id': i} for i in filtered_df.columns]
            end_time2 = time.time()
            time2 = end_time2 - end_time1

            # Update graph
            #pivoted_df = pd.DataFrame.from_dict(pivoted_df)

            ctd_fig = go.Figure(original_ctd_fig)
            particles_fig = go.Figure(original_particles_fig)
            tag_t_fig = go.Figure(original_tag_t_fig)
            #feat_fig = go.Figure(original_features_fig)
            object_ids = data_df['obj_id'].tolist()
            # feat_fig = px.scatter(x=loaded_embedding[:, 0],
            #                 y=loaded_embedding[:, 1],
            #                 #mode='markers',
            #                 hover_name=object_ids,
            #                 #marker=dict(color='blue'),
            #                 render_mode='svg',
            #                 )
            #feat_fig = original_features_fig

            # Add horizontal line to figures
            ctd_fig.add_hline(y=updated_pressure, line_width=3, line_dash="dash", line_color="red")
            particles_fig.add_hline(y=updated_pressure, line_width=3, line_dash="dash", line_color="red")
            tag_t_fig.add_hline(y=updated_pressure, line_width=3, line_dash="dash", line_color="red")

            #Add selected obj features to feature plot
            sel_objs = filtered_df['obj_id'].tolist()
            indices = filtered_df['index'].tolist()
            sel_x = filtered_df['umap_x'].tolist()
            sel_y = filtered_df['umap_y'].tolist()
            print(len(indices),len(sel_x))
            sel_features_fig = px.scatter(
                            x= sel_x,
                            y= sel_y,
                            #mode='markers',
                            hover_name=sel_objs,
                            color_discrete_sequence=['red'],
                            render_mode='svg',
                            )
            upd_feat_fig = original_features_fig.add_trace(sel_features_fig.data[0])
            temp_features_fig = upd_feat_fig

            # Convert figures back to dictionaries
            upd_ctd_fig = ctd_fig.to_dict()
            upd_particles_fig = particles_fig.to_dict()
            upd_tag_t_fig = tag_t_fig.to_dict()
            upd_feat_fig = upd_feat_fig.to_dict()

            #_, pivoted_df = populate_esd_bins_pressure(full_df, depth_bin_size=depth_bin_size, esd_bins=np.array([0,125,250,500,1000,100000]))
            end_time3 = time.time()
            time3 = end_time3 - end_time2
            #upd_ctd_fig = plot_ctd_data(pd.DataFrame(data), selected_pressure=updated_pressure)
            #upd_particles_fig = plot_particles_distribution(grouped=pivoted_df, selected_pressure=updated_pressure)
            end_time4 = time.time()
            time4 = end_time4 - end_time3
            ctd_click = None
            return upd_ctd_fig, updated_img_fig, upd_particles_fig, upd_tag_t_fig, upd_feat_fig, updated_pressure, filtered_df.to_dict('records'), columns, f"selected image: {os.path.basename(image_name)}", [idx_unique_df], page_number
        
        if ctd_relayout_data is not None and 'yaxis.range[0]' in ctd_relayout_data and 'yaxis.range[1]' in ctd_relayout_data:
            y_range = [ctd_relayout_data['yaxis.range[0]'], ctd_relayout_data['yaxis.range[1]']]

            particles_fig = go.Figure(particles_fig)
            particles_fig.update_yaxes(range=y_range, autorange=False)
            particles_fig_dict = particles_fig.to_dict()

            tag_t_fig = go.Figure(tag_t_fig)
            tag_t_fig.update_yaxes(range=y_range, autorange=False)
            tag_t_fig_dict = tag_t_fig.to_dict()

            return dash.no_update, dash.no_update, particles_fig_dict, tag_t_fig_dict, dash.no_update, dash.no_update, dash.no_update, dash.no_update, f"zoomed to {y_range} ", dash.no_update, dash.no_update

    else:   
        # Return unchanged figures 
        return dash.no_update

#Crop Table Selection
@app.callback(
    [Output('crop', 'figure', allow_duplicate=True),
     Output('img', 'figure', allow_duplicate=True),
     Output('features', 'figure', allow_duplicate=True),],
    [Input('tbl_crops', 'selected_rows')],
    [State('tbl_crops', 'data')],
    prevent_initial_call=True
)
def update_crops(selected_crop, crop_data):
    global temp_features_fig
    if selected_crop:
        selected_row = crop_data[selected_crop[0]]
        image_name = selected_row['full_path']

        # Update image
        img = Image.open(image_name)
        upd_crop_fig = px.imshow(img, color_continuous_scale='gray', title=os.path.basename(image_name))

        ov_image_name = selected_row['overview_path']
        ov_img = Image.open(ov_image_name)
        overview_fig = px.imshow(ov_img, title=os.path.basename(ov_image_name))

        #overview_fig = go.Figure(overview_fig)
        
        ## Bounding Box on overview image
        # Scale factors
        scale_x = 1280 / 2560
        scale_y = 1280 / 2560
        overview_fig.add_shape(
        # Rectangle type
        type="rect",
        # x-reference is assigned to the x-values
        xref="x",
        # y-reference is assigned to the y plot
        yref="y",
        # Top left corner coordinates
        x0=(selected_row['x']- selected_row['w']/2) * scale_x,
        y0=(selected_row['y']- selected_row['h']/2) * scale_y,
        # Bottom right corner coordinates
        x1=(selected_row['x'] + selected_row['w']/2) * scale_x,
        y1=(selected_row['y'] + selected_row['h']/2) * scale_y,
        # Line properties
        line=dict(
            color="Red",
            width=2,
        ),
        # Fill properties
        fillcolor="LightSkyBlue",
        opacity=0.5,
    )
    
        idx = selected_row['index']
        sel_crop_fig = px.scatter(x=[loaded_embedding[idx, 0]],y=[loaded_embedding[idx, 1]], render_mode='svg', color_discrete_sequence=['green'], hover_name=[selected_row['obj_id']])  
        upd_features_fig = temp_features_fig.add_trace(sel_crop_fig.data[0])
        return upd_crop_fig, overview_fig, upd_features_fig

    else:
        # Return unchanged figures 
        return crop_fig,     

#Feature Plot crop selection
@app.callback(
    [Output('crop', 'figure', allow_duplicate=True),
    Output('img', 'figure', allow_duplicate=True),
    Output('ctd', 'figure', allow_duplicate=True),
    Output('particles', 'figure', allow_duplicate=True),
    Output('features', 'figure', allow_duplicate=True),
    Output('tbl_crops', 'data', allow_duplicate=True),
    Output('tbl_crops', 'columns', allow_duplicate=True),],
    [Input('features','clickData')],
    prevent_initial_call=True
)
def update_feature_selection(feat_click):
    global original_df
    global original_ctd_fig
    global original_particles_fig
    global temp_features_fig
    global loaded_relock_embedding
    global loaded_normal_embedding
    global loaded_obj_ids

    if feat_click is not None:
        print(feat_click)
        obj_id = feat_click['points'][0]['hovertext']
        selected_row = original_df[original_df['obj_id']==obj_id]
        print(selected_row)
        image_name = selected_row['full_path'].values[0]
        obj_id = selected_row['obj_id'].values[0]
        print(image_name, obj_id)

        # Update image
        img = Image.open(image_name)
        upd_crop_fig = px.imshow(img, color_continuous_scale='gray', title=obj_id)

        ov_image_name = selected_row['overview_path'].values[0]
        ov_img = Image.open(ov_image_name)
        overview_fig = px.imshow(ov_img, title=os.path.basename(ov_image_name))
        
        ## Bounding Box on overview image
        # Scale factors
        scale_x = 1280 / 2560
        scale_y = 1280 / 2560
        overview_fig.add_shape(
            # Rectangle type
            type="rect",
            # x-reference is assigned to the x-values
            xref="x",
            # y-reference is assigned to the y plot
            yref="y",
            # Top left corner coordinates
            x0=(selected_row['x'].values[0]- selected_row['w'].values[0]/2) * scale_x,
            y0=(selected_row['y'].values[0]- selected_row['h'].values[0]/2) * scale_y,
            # Bottom right corner coordinates
            x1=(selected_row['x'].values[0] + selected_row['w'].values[0]/2) * scale_x,
            y1=(selected_row['y'].values[0] + selected_row['h'].values[0]/2) * scale_y,
            # Line properties
            line=dict(
                color="Red",
                width=2,
            ),
            # Fill properties
            fillcolor="LightSkyBlue",
            opacity=0.5,
        )

        updated_pressure = selected_row['pressure [dbar]'].values[0]       

        # Filter the DataFrame based on the selected date-time
        selected_datetime = selected_row['date-time'].values[0]
        full_df = original_df
        filtered_df = full_df[full_df['date-time'] == selected_datetime]
        columns = [{'name': i, 'id': i} for i in filtered_df.columns]
        

        # Update graph

        ctd_fig = go.Figure(original_ctd_fig)
        particles_fig = go.Figure(original_particles_fig)
        
        #object_ids = full_df['obj_id'].tolist()
        obj_ids = loaded_obj_ids
        print(len(obj_ids), len(loaded_normal_embedding))
        feat_fig = px.scatter(x=loaded_normal_embedding[:, 0],
                        y=loaded_normal_embedding[:, 1],
                        #mode='markers',
                        hover_name=obj_ids,
                        #marker=dict(color='blue'),
                        render_mode='svg',
                        )

        # Add horizontal line to figures
        ctd_fig.add_hline(y=updated_pressure, line_width=3, line_dash="dash", line_color="red")
        particles_fig.add_hline(y=updated_pressure, line_width=3, line_dash="dash", line_color="red")

        #Add selected obj features to feature plot
        sel_objs = filtered_df['obj_id'].tolist()
        #indices = filtered_df['index'].tolist()
        sel_x = filtered_df['umap_x'].tolist()
        sel_y =filtered_df['umap_y'].tolist()
        #print(len(indices),len(sel_x))
        sel_features_fig = px.scatter(
                        x= sel_x,
                        y= sel_y,
                        #mode='markers',
                        hover_name=sel_objs,
                        color_discrete_sequence=['red'],
                        render_mode='svg',
                        )
        # idx = selected_row['index'].values[0]
        # print(loaded_embedding[idx,0],loaded_embedding[idx,1])
        sel_crop_fig = px.scatter(x=selected_row['umap_x'].tolist(),y=selected_row['umap_y'].tolist(), render_mode='svg', color_discrete_sequence=['green'], hover_name=[selected_row['obj_id'].values[0]])
        upd_feat_fig = feat_fig.add_trace(sel_features_fig.data[0])
        upd_feat_fig = upd_feat_fig.add_trace(sel_crop_fig.data[0])
        temp_features_fig = upd_feat_fig

        # Convert figures back to dictionaries
        upd_ctd_fig = ctd_fig.to_dict()
        upd_particles_fig = particles_fig.to_dict()
        upd_feat_fig = upd_feat_fig.to_dict()

        return upd_crop_fig, overview_fig, upd_ctd_fig, upd_particles_fig, upd_feat_fig, filtered_df.to_dict('records'), columns,

    else:
        # Return unchanged figures 
        return crop_fig,     

if __name__ == '__main__':
    app.run(debug=True, host='10.136.72.201', port=8050)
