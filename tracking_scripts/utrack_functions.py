# -*- coding: utf-8 -*-
# utrack_functions.py --> functions to calculate moisture footprints
import os
import sys
import settings
import operator
import xarray as xr
import numpy as np
import pandas as pd


# Function that returns index of closest latitude in the tracking array
# to the one provided by the tracking zone
def get_closest_index(lats, lat):
    lat_index, min_value = min(
        enumerate(abs(lats-lat)),
        key=operator.itemgetter(1)
    )
    return lat_index


# Get monthly moisture footprints (forwards & backwards)
def track_footprints(month, latitude, longitude, evap, precip, grid_area):
    # Create lat,lon arrays equal to dimensions of tracking dataset
    lats = np.arange(90, -90, -0.5)
    lons = np.arange(0, 360, 0.5)
    latidx = get_closest_index(lats, latitude)
    lonidx = get_closest_index(lons, longitude)
    # UTrack atmospheric moisture trajectory dataset
    UTrack = xr.open_dataset(
        os.path.join(
            settings.PATH_UTRACK,
            'utrack_climatology_0.5_' + str(month).zfill(2)+'.nc'
        )
    ).moisture_flow

    # Forward tracking footprint
    fp_fw = UTrack[latidx, lonidx, :, :].values
    fp_fw = fp_fw * -0.1
    fp_fw = np.e**fp_fw
    fp_fw[fp_fw == 1] = 0
    forward_fp = fp_fw / np.nansum(fp_fw)
    # print('FW_Footprint: This values should always be 1 ',
    # np.nansum(forward_fp).round(2), --> , np.nansum(forward_fp))
    ET_source = (
        (
            (evap[month-1])[latidx, lonidx].values
        ) * (
            grid_area[latidx, lonidx].values
        )
    )
    forward_fp = forward_fp * ET_source
    # Backward tracking footprint
    fp_bw = UTrack[:, :, latidx, lonidx].values
    fp_bw = fp_bw * -0.1
    fp_bw = np.e**fp_bw
    fp_bw[fp_bw == 1] = 0
    ET = (evap[month-1]).values
    # backward_fp = fp_bw * ET
    fp_bw = ET * fp_bw
    backward_fp = fp_bw / np.nansum(fp_bw)
    # # print('BW_Footprint: This values should always be 1 ',
    # 'np.nansum(backward_fp).round(2), --> , np.nansum(bw_footprint))
    P_sink = (precip[month-1])[latidx, lonidx].values * grid_area[latidx, lonidx].values
    backward_fp = backward_fp * P_sink

    return forward_fp, backward_fp


# Runner Function: Takes DataFrame with lons,lats and aggregates footprints
#   for each sink/source cell given by (lon,lat) for each month (1-12)
# output: --> Datasets containing monthly moisture footprints
def moisture_tracking_runner(Screened_data):
    # Load evaporation and precipitation data
    evap = xr.open_dataset(
        os.path.join(settings.PATH_DATA_ERA5_E)
        ).e.sel(
            time=slice('2008-01-01', '2017-12-01')
        )
    # Convert to multi-year mean
    evap = evap.groupby('time.month').mean(dim='time')
    evap = (xr.where(evap > 0, evap, 0))

    precip = xr.open_dataset(
        os.path.join(settings.PATH_DATA_ERA5_P)
        ).tp.sel(
        time=slice('2008-01-01', '2017-12-01')
        )
    # Convert to multi-year mean
    precip = precip.groupby('time.month').mean(dim='time')
    precip = (xr.where(precip > 0, precip, 0))

    # Water balance correction step 1 
    # ALPHA calculated in: bgwater/papers/paper_III/Elena_comparison/ERA5_water_balance.py
    if settings.apply_correction == True:

        # Correction factors of 10yr ERA5 mean
        alpha_precip = settings.alpha_precip
        alpha_evap = settings.alpha_evap
        
        precip = precip * alpha_precip
        evap = evap * alpha_evap

    else:
        pass
    
    # Load grid_area in m2 to convert footprints from mm to litres
    grid_area = xr.open_dataset(settings.GRID_PATH, engine='netcdf4').cell_area

    Forward_footprint_monthly_final = np.zeros(shape=(12, 360, 720))
    Backward_footprint_monthly_final = np.zeros(shape=(12, 360, 720))
    for j in range(Screened_data.shape[0]):  # iterate over source/sink cells
        latitude, longitude = np.array(Screened_data.loc[j])
        Forward_footprint_monthly = np.zeros(shape=(12, 360, 720))
        Backward_footprint_monthly = np.zeros(shape=(12, 360, 720))

        for i in range(12):  # iterate over months (1:12)
            Forward_footprint_monthly[i, :, :], Backward_footprint_monthly[i, :, :] = track_footprints(i+1, latitude, longitude, evap, precip, grid_area)
        Forward_footprint_monthly = np.where(
            np.isnan(Forward_footprint_monthly),
            0,
            Forward_footprint_monthly
        )
        Backward_footprint_monthly = np.where(
            np.isnan(Backward_footprint_monthly),
            0,
            Backward_footprint_monthly
        )
        Forward_footprint_monthly_final = Forward_footprint_monthly_final + Forward_footprint_monthly
        Backward_footprint_monthly_final = Backward_footprint_monthly_final + Backward_footprint_monthly

    # write monthly footprints into dataset
    Forward_footprint_monthly_sum = xr.DataArray(
        Forward_footprint_monthly_final,
        coords=[evap.month.values, evap.lat.values, evap.lon.values],
        dims=['month', 'lat', 'lon'],
        name="fw_evap_footprint_monthly",
        attrs=dict(
            description="Forward Monthly Evaporation Footprint",
            units="l/month"
        )
    )
    Backward_footprint_monthly_sum = xr.DataArray(
        Backward_footprint_monthly_final,
        coords=[evap.month.values, evap.lat.values, evap.lon.values],
        dims=['month', 'lat', 'lon'],
        name="bw_evap_footprint_monthly",
        attrs=dict(
            description="Backward Monthly Evaporation Footprint",
            units="l/month"
        )
    )
    return Forward_footprint_monthly_sum, Backward_footprint_monthly_sum
