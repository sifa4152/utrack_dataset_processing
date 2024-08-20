# =============================================================================
# UTrack tracking post-processing script to calculate atmospheric watersheds
# prequisite --> assembled runs (assemble_runs.py)
# requires filepaths as in settings.py
# calculates atmospheric watersheds from backward and forward footprints
# rewritten: 07/08/2024
# parallel processing added: 18/08/2024
# S. F. Fahrländer, Potsdam Institute for Climate Impact Research
# =============================================================================
# load libraries
import os
import sys
import numpy as np
import pandas as pd
import xarray as xr
from tqdm import tqdm

from affine import Affine
import rasterio
from rasterio.transform import from_origin
import geopandas as gpd
from shapely.geometry import shape
from rasterio.features import shapes

from shapely.geometry import shape, MultiPolygon
from shapely.ops import unary_union
from concurrent.futures import ProcessPoolExecutor


# =============================================================================
# function to define the cells that fall into the X-pshed
# input: target percent of pshed, 100% precipitationshed as DataArray
# output: last counted cell falling into X-pshed
def pshed_limit_counter(percent, pshed):
    pshed100 = np.nansum(pshed)  # total precipitation amount
    percentile = percent/100
    pshedX = pshed100*percentile  # X% precipitation amount
    # flatten and sort pshed-array
    pshed100_copy = np.copy(pshed)
    pshed100_flat = pshed100_copy.flatten()
    pshed100_sort = np.sort(pshed100_flat)
    pshed100_sort = np.flip(pshed100_sort)  # flattend and sorted (high to low)
    i = 0
    psum = 0
    while psum < pshedX:
        psum = psum + pshed100_sort[i]
        i = i + 1
        # print(i)
    return i


# =============================================================================
# function that creates pshed-mask as matrix of 0-1
# input: precipitationshed as DataArray, output from pshed_limit_counter()
# output: mask of X-pshed [0-1]
def pshed_matrix(pshed, last_cell):
    pshed_copy = np.copy(pshed)
    pshed_flat = pshed_copy.flatten()
    pshed_sort = np.sort(pshed_flat)
    pshed_sort = np.flip(pshed_sort)
    pshedX_matrix = np.copy(pshed_copy)
    lat = pshed.lat
    row = np.arange(0, len(lat), 1)
    lon = pshed.lon
    col = np.arange(0, len(lon), 1)
    for j in row:
        for k in col:
            if pshedX_matrix[j, k] >= pshed_sort[last_cell]:
                pshedX_matrix[j, k] = 1
            else:
                pshedX_matrix[j, k] = float('nan')
    return pshedX_matrix


# =============================================================================
# function to create and extract X-pshed mask and values
# input: file_path to 100% pshed, percent X
# output: mask and value array of X-pshed --> (mask,values)
# direction: backward --> Pshed, forward --> Eshed
def percentile_pshed(input_fp, percent, direction, transform=False):
    # load evaporation footprint
    if direction == 'backward':
        shed = xr.open_dataset(input_fp, engine='netcdf4')['bw_evap_footprint_monthly']
    else:  # elif direction == 'forward':
        shed = xr.open_dataset(input_fp, engine='netcdf4')['fw_evap_footprint_monthly']

    # aggregate to annual average
    shed = shed.sum(dim='month', skipna=True)
    # define last counted cell for shed
    last_cell = pshed_limit_counter(percent, shed)
    # create shed matrix
    shedX_matrix = pshed_matrix(shed, last_cell)
    # create mask (0-1)
    if direction == 'backward':
        shedX_mask = xr.DataArray(
            shedX_matrix, coords=[shed.lat.values, shed.lon.values],
            dims=['lat', 'lon'],
            name=f'{percent}%_pshed_mask',
            attrs=dict(description="Mask of Percentile Precipitationshed",
                       units="[0-1]")
                )

    else:  # if direction == 'forward':
        shedX_mask = xr.DataArray(
            shedX_matrix, coords=[shed.lat.values, shed.lon.values],
            dims=['lat', 'lon'],
            name=f'{percent}%_eshed_mask',
            attrs=dict(description="Mask of Percentile Evaporationtionshed",
                       units="[0-1]")
            )
    # create value array
    shedX_values = shed*shedX_mask

    if direction == 'backward':
        shedX_values = shedX_values.rename(f'{percent}%_pshed_values')
    if direction == 'forward':
        shedX_values = shedX_values.rename(f'{percent}%_eshed_values')

    # transform coordinates from UTrack to (lon:(-180,180), lat(-89.5,90))
    if transform is True:
        # reset coordinates
        shedX_mask.coords['lon'] = (shedX_mask.coords['lon'] + 180) % 360 - 180
        shedX_mask = shedX_mask.sortby(shedX_mask.lon)
        shedX_mask = shedX_mask.reindex(lat=list(reversed(shedX_mask.lat))) # deactivated due to reindexing error
        shedX_mask.rio.write_crs("epsg:4326", inplace=True)

        shedX_values.coords['lon'] = (shedX_values.coords['lon'] + 180) % 360 - 180
        shedX_values = shedX_values.sortby(shedX_values.lon)
        shedX_values = shedX_values.reindex(lat=list(reversed(shedX_values.lat))) # deactivated due to reindexing error
        shedX_values.rio.write_crs("epsg:4326", inplace=True)
        
    # combine mask and value arrays to dataset
    combined_ds = xr.merge([shedX_values, shedX_mask])

    return combined_ds  # shedX_mask, shedX_values


# =============================================================================
# function to delineate atmospheric watersheds and save as netcdf
# INPUT: list or df of ids, percent of total moisture accounted for watersheds
def atmos_watersheds_netcdf(idx, percent):
    # Precipitation- and Evaporationsheds
    try:
        bw_path = os.path.join(
            settings.TOTAL_BACKWARD,
            f'backward_footprint_{idx}.nc'
            )
    except FileNotFoundError:
        bw_path = f'missing bw_footprint: {idx} --> moving on...'
        print(bw_path)
    try:
        fw_path = os.path.join(
            settings.TOTAL_FORWARD,
            f'forward_footprint_{idx}.nc'
            )
    except FileNotFoundError:
        fw_path = f'missing fw_footprint: {idx} --> moving on...'
        print(fw_path)

    pshed = percentile_pshed(
        bw_path, percent,
        direction='backward',
        transform=True)
    eshed = percentile_pshed(
        fw_path,
        percent,
        direction='forward',
        transform=True)

    pshed.to_netcdf(
        os.path.join(settings.PSHED_PATH, f'pshed{percent}_{idx}.nc'),
        engine='netcdf4'
        )
    eshed.to_netcdf(
        os.path.join(settings.ESHED_PATH, f'eshed{percent}_{idx}.nc'),
        engine='netcdf4'
        )

        # print(f'zone: {idx} --> [{count+1}/{len(ID)}]')


# =============================================================================
# function to derive the affine transform from an xarray DataArray with latitude and longitude coordinates
def derive_transform(data_array):
    """
    Derive the affine transform from an xarray DataArray with latitude and longitude coordinates.
    """
    # Assuming the DataArray has 2D coordinates 'latitude' and 'longitude'
    lat = data_array['lat'].values
    lon = data_array['lon'].values

    # Calculate the pixel size assuming regular spacing
    pixel_size_lat = np.abs(lat[1] - lat[0])
    pixel_size_lon = np.abs(lon[1] - lon[0])

    # Create the transform: from_origin expects upper-left corner coordinates and pixel sizes
    transform = from_origin(west=lon.min(), north=lat.max(), xsize=pixel_size_lon, ysize=pixel_size_lat)

    return transform


# =============================================================================
# function to convert an xarray DataArray to a GeoDataFrame
def array_to_geodataframe(data_array, transform):
    """
    Convert an xarray DataArray to a GeoDataFrame
    """
    if not isinstance(data_array, xr.DataArray):
        raise ValueError("Input is not an xarray DataArray")

    data = data_array.values.astype(np.float32)  # Cast to float32
    mask = np.isfinite(data)  # Assuming non-NaN values are valid

    shapes_gen = shapes(data, mask=mask, transform=transform)
    records = [{"geometry": shape(geom), "value": value} for geom, value in shapes_gen if value > 0]
    gdf = gpd.GeoDataFrame.from_records(records)
    
    # Merge all geometries into a single shape
    if not gdf.empty:
        merged_geometry = unary_union(gdf.geometry)
        gdf = gpd.GeoDataFrame(geometry=[merged_geometry])
    
    return gdf

# =============================================================================
# function to delineate atmospheric watersheds and save as GeoJSON
def atmos_watersheds_geojson(idx, percent):
    try:
        bw_path = os.path.join(settings.TOTAL_BACKWARD, f'backward_footprint_{idx}.nc')
        fw_path = os.path.join(settings.TOTAL_FORWARD, f'forward_footprint_{idx}.nc')
    except FileNotFoundError:
        print(f'Missing footprint for zone {idx} --> moving on...')
        return
    
    try:
        pshed = percentile_pshed(bw_path, percent, direction='backward', transform=False)
        eshed = percentile_pshed(fw_path, percent, direction='forward', transform=False)
    except Exception as e:
        print(f'Error processing zone {idx}: {e}')
        return

    pshed_values = pshed[f'{percent}%_pshed_values']
    eshed_values = eshed[f'{percent}%_eshed_values']
    
    transform = derive_transform(pshed_values)
    
    try:
        pshed_gdf = array_to_geodataframe(pshed_values, transform)
        eshed_gdf = array_to_geodataframe(eshed_values, transform)
        
        if pshed_gdf.empty or eshed_gdf.empty:
            print(f'No geometries found for zone {idx} --> moving on...')
            return
    except AttributeError as e:
        print(f'AttributeError: {e} --> skipping zone {idx}')
        return

    # Save as GeoJSON
    pshed_gdf.to_file(os.path.join(settings.PSHED_PATH, f'pshed{percent}_{idx}_values.geojson'), driver='GeoJSON')
    eshed_gdf.to_file(os.path.join(settings.ESHED_PATH, f'eshed{percent}_{idx}_values.geojson'), driver='GeoJSON')


# =============================================================================
if __name__ == '__main__':
    # sys.path.insert(1, '/p/projects/open/simon/bgwater/GCEW/final_report/global_basin_utrack_runs/2024_08_13_basins_selected/watershed_processing')
    import settings

    params = pd.read_csv(settings.PARAMS, index_col=0)
    zone_ids = params.zone.drop_duplicates().reset_index(drop=True)
    # zone_ids = zone_ids[:5]  # testing array
    percentile = settings.PERCENTILE
    output_format = settings.OUTPUT_FORMAT
    max_workers = settings.MAX_WORKERS
    
    # NetCDF output
    if output_format == 'netcdf':
        # Parallel processing with X CPUs
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            list(tqdm(executor.map(atmos_watersheds_netcdf, zone_ids, [percentile] * len(zone_ids)), total=len(zone_ids)))
    
    # GeoJSON output
    elif output_format == 'geojson':
        # Parallel processing with X CPUs
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            list(tqdm(executor.map(atmos_watersheds_geojson, zone_ids, [percentile] * len(zone_ids)), total=len(zone_ids)))

