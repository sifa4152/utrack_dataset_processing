# =============================================================================
# ASSEMBLE CLUSTER JOBS
# --> load filepaths via settings.py
# updated: 06/06/2023
# =============================================================================
import os
import sys
import glob
import pandas as pd
import numpy as np
import xarray as xr
from tqdm import tqdm
import settings
from utils import ensure_output_directory

# =============================================================================
def assemble_job_arrays(zone_id):
    for count, id in enumerate(tqdm(zone_id)):
        # print(f'{id} -> [{count+1}/{len(zone_id)}]')
        fw_files = glob.glob(
            os.path.join(settings.PATH_MOISTURE_FOOTPRINTS,'forward', f'forward_footprint_{id}_*.nc')
            )
        bw_files = glob.glob(
            os.path.join(settings.PATH_MOISTURE_FOOTPRINTS, 'backward', f'backward_footprint_{id}_*.nc')
            )

        if not fw_files:
            continue

        fw_sum = np.zeros(shape=(12, 360, 720))
        fw_sum_final = np.zeros(shape=(12, 360, 720))

        bw_sum = np.zeros(shape=(12, 360, 720))
        bw_sum_final = np.zeros(shape=(12, 360, 720))

        for i, j in zip(fw_files, bw_files):
            fw = xr.open_dataset(i, engine='netcdf4')['fw_evap_footprint_monthly']
            bw = xr.open_dataset(j, engine='netcdf4')['bw_evap_footprint_monthly']
            fw = xr.where(fw == np.nan, 0, fw)
            bw = xr.where(bw == np.nan, 0, bw)

            fw_sum_final = fw_sum_final + fw.values
            bw_sum_final = bw_sum_final + bw.values

        fw_assembled = xr.DataArray(
            fw_sum_final,
            coords=[fw.month.values, fw.lat.values, fw.lon.values],
            dims=['month', 'lat', 'lon'],
            name="fw_evap_footprint_monthly",
            attrs=dict(description="Forward Monthly Evaporation Footprint",
                       units="l/month")
            )
        bw_assembled = xr.DataArray(
            bw_sum_final,
            coords=[fw.month.values, fw.lat.values, fw.lon.values],
            dims=['month', 'lat', 'lon'],
            name="bw_evap_footprint_monthly",
            attrs=dict(description="Backward Monthly Evaporation Footprint",
                       units="l/month")
            )
        out_dir_esheds = ensure_output_directory(settings.PATH_MOISTURE_FOOTPRINTS, 'forward_complete')
        out_dir_psheds = ensure_output_directory(settings.PATH_MOISTURE_FOOTPRINTS, 'backward_complete')
        
        fw_assembled.to_netcdf(
            os.path.join(out_dir_esheds,
                         f'forward_footprint_{id}.nc'), engine='netcdf4')
        bw_assembled.to_netcdf(
            os.path.join(out_dir_psheds,
                         f'backward_footprint_{id}.nc'), engine='netcdf4')


if __name__ == '__main__':

    params = pd.read_csv(settings.PARAMS, index_col=0)
    zone_id = params.zone.drop_duplicates().reset_index(drop=True)

    assemble_job_arrays(zone_id)
