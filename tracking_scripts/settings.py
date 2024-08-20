# -*- coding: utf-8 -*-
# settings.py containing filepaths and settings for tracking routine
import os

# Working directory
WRKDIR = os.path.join('working_dir_with_tracking_scripts') 

# Output directory  
PATH_MOISTURE_FOOTPRINTS = os.path.join('output','moisture_footprints')

# Parameters for submission of job packages
PARAMS = os.path.join(WRKDIR,'params.csv') 


# Input data
## evaporation (file)
PATH_DATA_ERA5_E = os.path.join('data','era5_reanalysis','era5_evaporation','era5_monthly_evap_1979_2021_mm_month_remap.nc') 

## precipitation (file)
PATH_DATA_ERA5_P = os.path.join('data','era5_reanalysis','era5_precipitation','era5_monthly_tp_1979_2021_mm_month_remap.nc') 

## utrack climatology (folder)
PATH_UTRACK = os.path.join('data','UTrack_global_moisture_fluxes')

## ERA5 grid area (file)
GRID_PATH = os.path.join('data','era5_reanalysis', 'era5_grid_area','era5_grid_area_m2_utrack.nc')

## location of target cell coordinates (folder)
PATH_TARGET_ZONES = os.path.join('data','study_regions','countries','CNTR_OC_mask_EUROSTAT_GOaS','target_cells')


# Settings
## Apply ERA5 water balance correction (2008-2017) [True/False]
apply_correction = True

## Correction factors of 10yr ERA5 mean 
alpha_precip = 0.9971611782286123
alpha_evap = 1.0028752465214772
