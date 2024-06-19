# -*- coding: utf-8 -*-
# main.py --> runner for UTrack dataset processing
import os
import sys
import pandas as pd
from utrack_functions import moisture_tracking_runner
from utils import ensure_output_directory
import settings


def job_runner():

    # first parameter is job id
    if len(sys.argv):
        job_id = int(sys.argv[1])
    else:
        raise Exception('job_id (int) is needed as argument.')

    assert isinstance(job_id, int)

    df_params = pd.read_csv(settings.PARAMS, index_col=0)
    params = df_params.iloc[job_id-1]
    start = params['start']
    stop = params['stop']
    zone = params['zone']

    ## load target cells
    path_target_cells = os.path.join(settings.PATH_TARGET_ZONES, f'target_cells_{zone}.csv')
    screened_data = pd.read_csv(path_target_cells, index_col=0)
    screened_data = screened_data.iloc[start:stop].reset_index(drop=True)
    
## run tracking
    forward, backward = moisture_tracking_runner(screened_data)
    
## save output
    out_dir_esheds = ensure_output_directory(settings.PATH_MOISTURE_FOOTPRINTS, 'forward')
    out_dir_psheds = ensure_output_directory(settings.PATH_MOISTURE_FOOTPRINTS, 'backward')
    
    fw_path = os.path.join(out_dir_esheds, f'forward_footprint_{zone}_{start}_{stop}.nc')
    bw_path = os.path.join(out_dir_psheds, f'backward_footprint_{zone}_{start}_{stop}.nc')

    forward.to_netcdf(fw_path, engine='netcdf4')
    backward.to_netcdf(bw_path, engine='netcdf4')

if __name__ == '__main__':
    job_runner()