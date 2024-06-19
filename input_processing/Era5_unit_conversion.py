# =============================================================================
# ERA5 REANALYSIS UNIT CONVERSION from m of water equivalent per day to mm/month and mm/year
# Simon Felix Fahrlaender
# 14/11/2022
# =============================================================================
import os
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
# =============================================================================
## function to convert ERA5 evaporation data from m of water equivalent to mm/month and mm/yr
def ERA5_evaporation_conversion(era5_data):
    ## check dimensions
    if (era5_data.dims == ('time', 'lat', 'lon')) == False:
        raise Exception('Dimensions are incorrect!')
    
    ## extract data attributes
    attr = era5_data.attrs

    ## extract days of each month in dataset
    days_in_month = (era5_data['time'].dt.days_in_month).values

    ## create a weighing array in the same shape as the dataset
    weighing = np.ones(era5_data.shape)
    for i in range(era5_data.shape[0]):
        weighing[i, :, :] = weighing[i, :, :]*days_in_month[i]

    ## convert dataset from 'm of water equivalent per day' to 'mm per month'
    era5_data_monthly_mm = era5_data*(-1000)*weighing
    attr['units'] = 'mm/month'
    era5_data_monthly_mm = era5_data_monthly_mm.assign_attrs(attr)

    ## resample dataset to annual means
    era5_data_annual_mm = era5_data_monthly_mm.resample(time='Y').sum(skipna=True)
    attr['units'] = 'mm/yr'
    era5_data_annual_mm = era5_data_annual_mm.assign_attrs(attr)

    return era5_data_monthly_mm, era5_data_annual_mm
# =============================================================================
## function to convert ERA5 precipitation data from m of water equivalent to mm/month and mm/yr
def ERA5_precipitation_conversion(era5_data):
    ## check dimensions
    if (era5_data.dims == ('time', 'lat', 'lon')) == False:
        raise Exception('Dimensions are incorrect!')
    
    ## extract data attributes
    attr = era5_data.attrs

    ## extract days of each month in dataset
    days_in_month = (era5_data['time'].dt.days_in_month).values

    ## create a weighing array in the same shape as the dataset
    weighing = np.ones(era5_data.shape)
    for i in range(era5_data.shape[0]):
        weighing[i, :, :] = weighing[i, :, :]*days_in_month[i]

    ## convert dataset from 'm of water equivalent per day' to 'mm per month'
    era5_data_monthly_mm = era5_data*(1000)*weighing
    attr['units'] = 'mm/month'
    era5_data_monthly_mm = era5_data_monthly_mm.assign_attrs(attr)

    ## resample dataset to annual means
    era5_data_annual_mm = era5_data_monthly_mm.resample(time='Y').sum(skipna=True)
    attr['units'] = 'mm/yr'
    era5_data_annual_mm = era5_data_annual_mm.assign_attrs(attr)

    return era5_data_monthly_mm, era5_data_annual_mm
# =============================================================================
if __name__ == '__main__':
    """
    ERA5 Reanalysis Flux Unit Conversion from (m of water equivalent per day) to (mm/month) and (mm/year):
    """
    # Define working directory and input file path 
    wrkdir = os.path.join('')
    filename = 'era5_evaporation_precipitation_1979_2021.nc'
    
    # Load ERA5 Reanalysis data (here tp and e in one file)
    PATH_era5_original = os.path.join(wrkdir,filename)
    era5_original = xr.open_dataset(PATH_era5_original, engine='netcdf4')
    era5_e = era5_original.e
    era5_tp = era5_original.tp
    
    ## EVAPORATION
    era5_e_mm_month, era5_e_mm_yr = ERA5_evaporation_conversion(era5_e)
    
    ## PRECIPITATION
    era5_tp_mm_month, era5_tp_mm_yr = ERA5_precipitation_conversion(era5_tp)
    
# =============================================================================
    # Control plots
    
    ## EVAPORATION
    print("ERA5 EVAPORATION")
    era5_e_mm_month[0,:,:].plot()
    plt.show()
    era5_e_mm_yr[0,:,:].plot()
    plt.show()
    
    ## PRECIPITATION
    print("ERA5 PRECIPITATION")
    era5_tp_mm_month[0,:,:].plot()
    plt.show()
    era5_tp_mm_yr[0,:,:].plot()
    plt.show()
# =============================================================================
    print("Saving ERA5 data to netCDF files...")
    ## MONTHLY
    era5_e_mm_month.to_netcdf(os.path.join(wrkdir, 'era5_monthly_evap_1979_2021_mm_month.nc'))
    era5_tp_mm_month.to_netcdf(os.path.join(wrkdir, 'era5_monthly_tp_1979_2021_mm_month.nc'))
    ## ANNUAL
    era5_e_mm_yr.to_netcdf(os.path.join(wrkdir, 'era5_annual_evap_1979_2021_mm_year.nc'))
    era5_tp_mm_yr.to_netcdf(os.path.join(wrkdir, 'era5_annual_tp_1979_2021_mm_year.nc'))
# =============================================================================
    print("Done!")
    