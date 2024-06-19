# -*- coding: utf-8 -*-
# utilities for the tracking routine (screening, params_creator, ensure_output_directory)
import os
import sys
import glob
import settings
import numpy as np
import pandas as pd


## Screening function to isolate tracking zone coordinates in mask
def screening(mask):
    lat = []
    lon = []
    #screened_data = []
    for y in range(mask.shape[0]):
        for x in range(mask.shape[1]):
            if np.isnan(mask[y,x].values) == True:
                continue
            else:
                lat.append(round(float(mask[y,x].lat.values),2))
                lon.append(round(float(mask[y,x].lon.values),2))
                #screened_data.append(mask[y,x].values)
    
    # Extraxt the data as dataframe
    screened_data = pd.DataFrame({'Lat': lat,'Lon': lon}) #,'Screened': Screened_data
    return screened_data


## function that creates job packages for utrack cluster runs --> saved in .csv
def params_creator(files, STEP_SIZE):
    def get_ID(zone_ID):
        return zone_ID.get('zone')

    params = []
    for file in files:
        zone_id = int(file.split('_')[-1].split('.')[0])
        df = pd.read_csv(file, index_col=0)
        current_row = 0
        while current_row + STEP_SIZE < len(df):
            params.append({'zone': zone_id, 'start': current_row, 'stop': current_row + STEP_SIZE})
            current_row += STEP_SIZE
        params.append({'zone': zone_id, 'start': current_row, 'stop': len(df)})

    params.sort(key=get_ID)
    pd.DataFrame(params).to_csv(os.path.join(settings.WRKDIR,'params.csv'))
    
    print('############')
    print(f'Number of needed jobs: {len(params)}')
    print('Dont forget to adjust the slurm script before submission!')
    print('############')


# Function to check if the output directory exists, if not create it
def ensure_output_directory(base_path: str, foldername: str) -> str:
    """
    Ensure the output directory exists.
    """
    output_dir = os.path.join(base_path, foldername)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    print(f"Output will be saved to: {output_dir}")
    return output_dir
