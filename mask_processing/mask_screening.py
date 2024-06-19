# =============================================================================
## TARGET CELL SCREENING FOR LAT & LON OF STUDY REGIONS
## Simon Felix Fahrländer, PIK, BGWater Project 
## updated: 01/06/2023
# =============================================================================
import os 
import pandas as pd
import numpy as np
import xarray as xr
from multiprocessing import Pool

# =============================================================================
## Screening function to isolate tracking zone coordinates in mask
def screening(mask):
    lat = []
    lon = []
    ## iterate over all cells in df
    for y in range(mask.shape[0]):
        for x in range(mask.shape[1]):
            if np.isnan(mask[y,x].values): # Use np.isnan directly, it returns True or False
                continue
            else: # append coordinates to lists 
                lat.append(round(float(mask[y,x].lat.values), 2))
                lon.append(round(float(mask[y,x].lon.values), 2))
    
    # Extract the data as dataframe
    screened_data = pd.DataFrame({'Lat': lat, 'Lon': lon})
    return screened_data

# =============================================================================
## Extract mask and run through screening function --> PARALLEL RUNS
def screen_func(ID, zones_path, out_path):
    print(f'Processing zone: {ID}') 
    
    # Load zones.nc from specified path
    ZONES = xr.open_dataset(zones_path).Band1
    
    # Convert from global mask to zone-specific mask [nan:1]
    mask = xr.where(ZONES == ID, 1, np.nan)
    
    # Apply screening function to mask
    screened_data = screening(mask)
    
    # Export screened data (DataFrame of latitudes and longitudes) to CSV
    screened_data.to_csv(os.path.join(out_path, f'target_cells_{ID}.csv'))
    # return screened_data  # Optionally return screened data if needed for further processing

# =============================================================================
if __name__ == '__main__':
    # =============================================================================
    ## IDs to split up processes
    num_ids = [1]  # Identifiers of zones to process; needs to be adjusted to your zones.nc file
    
    # Define file paths
    zones_path = "path/to/zones.nc"  # Adjust path to your zones.nc file
    out_path = "path/to/output/target/cells/folder"  # Adjust path to your output folder
    
    print('Start parallel processing')
    KERNEL = 4  # Number of CPUs for processing
    with Pool(KERNEL) as pool:
        pool.starmap(screen_func, [(ID, zones_path, out_path) for ID in num_ids])
