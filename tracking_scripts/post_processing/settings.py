# =============================================================================
# FILEPATHS FOR UTRACK POST-PROCESSING
# --> contains filepaths for: atmos_watershed.py
# updated: 18/08/2024, simonfa, PIK
# =============================================================================
import os

# SETTINGS 
PERCENTILE = 99 # allocation of moisture to watersheds
OUTPUT_FORMAT = 'geojson' # 'geojson' or 'netcdf'


# PARAMETERS
PARAMS = os.path.join('/p', 'projects', 'open', 'simon', 'bgwater', 'GCEW', 'final_report', 'global_basin_utrack_runs', '2024_08_13_basins_selected', 'params.csv')


# INPUTS
LSM_PATH = os.path.join('/p', 'projects', 'open', 'simon', 'bgwater', 'data_repo', 'era5_reanalysis', 'era5_lsm', 'era5_lsm_remap_utrack.nc')
PATH_TARGET_ZONES = os.path.join('/p', 'projects', 'open', 'simon', 'bgwater', 'data_repo', 'study_regions', 'countries', 'CNTR_OC_mask_EUROSTAT_GOaS', 'CNTR_OC_mask_EUROSTAT_GOaS.nc')
GRID_PATH = os.path.join('/p', 'projects', 'open', 'simon', 'bgwater', 'data_repo', 'era5_reanalysis', 'era5_grid_area', 'era5_grid_area_m2_utrack.nc')
PRECIP_PATH = os.path.join('/p', 'projects', 'open', 'simon', 'bgwater', 'data_repo', 'era5_reanalysis', 'era5_precipitation', 'era5_monthly_tp_1979_2021_mm_month_remap.nc')
EVAP_PATH = os.path.join('/p','projects','open','simon','bgwater','data_repo','era5_reanalysis','era5_evaporation','era5_monthly_evap_1979_2021_mm_month_remap.nc') 


# FOOTPRINTS
PATH_MOISTURE_FOOTPRINTS = os.path.join('/p', 'projects', 'open', 'simon', 'bgwater', 'GCEW', 'final_report', 'global_basin_utrack_runs', '2024_08_13_basins_selected','moisture_footprints')
TOTAL_FORWARD = os.path.join(PATH_MOISTURE_FOOTPRINTS, 'forward_complete')
TOTAL_BACKWARD = os.path.join(PATH_MOISTURE_FOOTPRINTS, 'backward_complete')


# PROCESS OUTPUTS
OUT = os.path.join('/p', 'projects', 'open', 'simon', 'bgwater', 'GCEW', 'final_report', 'global_basin_utrack_runs', '2024_08_13_basins_selected', 'watershed_processing')

if OUTPUT_FORMAT == 'geojson':
    if not os.path.exists(os.path.join(OUT, 'esheds_geojson')):
        os.makedirs(os.path.join(OUT, 'esheds_geojson'))
        ESHED_PATH = os.path.join(OUT, 'esheds_geojson')
    if not os.path.exists(os.path.join(OUT, 'psheds_geojson')):
        os.makedirs(os.path.join(OUT, 'psheds_geojson'))
        PSHED_PATH = os.path.join(OUT, 'psheds_geojson')
        
elif OUTPUT_FORMAT == 'netcdf':
    if not os.path.exists(os.path.join(OUT, 'esheds_netcdf')):
        os.makedirs(os.path.join(OUT, 'esheds_netcdf'))
        ESHED_PATH = os.path.join(OUT, 'esheds_netcdf')
    if not os.path.exists(os.path.join(OUT, 'psheds_netcdf')):
        os.makedirs(os.path.join(OUT, 'psheds_netcdf'))
        PSHED_PATH = os.path.join(OUT, 'psheds_netcdf')
