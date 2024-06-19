# -*- coding: utf-8 -*-
# settings.py containing filepaths and settings for tracking routine
import os

# Working directory
WRKDIR = os.path.join('/p','projects','open','simon','bgwater','GCEW','final_report','NL_BE_case_study','2024_05_08_NL_BE_runs') 

# Output directory  
PATH_MOISTURE_FOOTPRINTS = os.path.join('/p','projects','open','simon','bgwater','GCEW','final_report','NL_BE_case_study','moisture_footprints','2024_05_08_NL_BE_runs')

# Parameters for submission of job packages
PARAMS = os.path.join('/p','projects','open','simon','bgwater','GCEW','final_report','NL_BE_case_study','2024_05_08_NL_BE_runs','params.csv') 


# Input data
## evaporation
PATH_DATA_ERA5_E = os.path.join('/p','projects','open','simon','bgwater','data_repo','era5_reanalysis','era5_evaporation','era5_monthly_evap_1979_2021_mm_month_remap.nc') 

## precipitation
PATH_DATA_ERA5_P = os.path.join('/p','projects','open','simon','bgwater','data_repo','era5_reanalysis','era5_precipitation','era5_monthly_tp_1979_2021_mm_month_remap.nc') 

## utrack climatology
PATH_UTRACK = os.path.join('/p','projects','open','simon','bgwater','data_repo','UTrack_global_moisture_fluxes')

## ERA5 grid area
GRID_PATH = os.path.join('/p','projects','open','simon','bgwater','data_repo','era5_reanalysis', 'era5_grid_area','era5_grid_area_m2_utrack.nc')

## location of target cell coordinates
PATH_TARGET_ZONES = os.path.join('/p','projects','open','simon','bgwater','data_repo','study_regions','countries','CNTR_OC_mask_EUROSTAT_GOaS','target_cells')


# Apply ERA5 water balance correction (2008-2017) [True/False]
apply_correction = True
# Correction factors of 10yr ERA5 mean 
alpha_precip = 0.9971611782286123
alpha_evap = 1.0028752465214772