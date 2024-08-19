# UTrack Database Moisture Tracking Routine

Simon F. Fahrländer, June 2024\
Potsdam Institute for Climate Impact Research - PIK

## Table of Contents

- [Description](#description)
- [Input Processing](#input-processing)
- [Mask Processing](#mask-processing)
- [UTrack Database Moisture Tracking](#utrack-database-moisture-tracking)
- [Post-Processing](#post-processing)

## Description

- This repository contains general routine scripts to post-process the UTrack climatology and extract moisture footprints for specific regions of interest

- The UTrack dataset has been developed by Tuinenburg et al. (2020) using the UTrack atmospheric moisture tracking model (Tuinenburg and Staal (2020)).
  - Tuinenburg, O. A., Theeuwen, J. J. E., &#38; Staal, A. (2020). High-resolution global atmospheric moisture connections from evaporation to precipitation. Earth System Science Data,12 (4), 3177–3188. <https://doi.org/10.5194/essd-12-3177-2020>
  - Tuinenburg, O. A., &#38; Staal, A. (2020). Tracking the global flows of atmospheric moisture and associated uncertainties. Hydrology and Earth System Sciences, 24(5), 2419–2435. <https://doi.org/10.5194/hess-24-2419-2020>

- Use cases, descriptions and reconciliation of tracking discrepancies to ERA5 forcing data:
  - Fahrländer, S. F., Wang‐Erlandsson, L., Pranindita, A., &#38; Jaramillo, F. (2024). Hydroclimatic Vulnerability of Wetlands to Upwind Land Use Changes. Earth’s Future, (3). <https://doi.org/10.1029/2023EF003837>
  - De Petrillo, E. & Fahrländer, S.F. , Tuninetti, M., Andersen, L.S., Monaco, L., Ridolfi, L., Laio, F., Reconciling tracked atmospheric water flows to close the global freshwater cycle, 29 April 2024, PREPRINT (Version 1) available at Research Square <https://doi.org/10.21203/rs.3.rs-4177311/v1>

- This version includes a water balance correction method in the moisture_tracking_runner() function in utrack_functions.py
  - the correction can be enabled and disabled via the 'apply_correction' flag in settings.py
  - the correction is applied to the monthly grouped ERA5 input data and multiplies the input data with the correction factor alpha
  - alpha = mean(P + E) / data and is calculated for each month separately in the following script: ERA5_water_balance.py
  - Normal input data for reference period 2008 - 2017
  - Output is in litres per year or litres per month (monthly output)

- Step-by-step instructions for the routine:
  1. Create Python environment (recommended: conda environment with environment.yml file)
  2. Process input data using ERA5_unit_conversion.py and retrace steps for water balance correction in ERA5_water_balance.py
  3. Process masks using shp2attr_raster.py and create csv files with coordinates for each mask
  4. Place mask and files in the correct directories and adjust settings.py
  5. Create job packages using create_params.py
  6. Test job runner using main.py, by e.g. --> `python3 main.py 1`
  7. Create hpc_out folder in WKDIR as output directory for SLURM error messages
  8. Submit jobs to HPC using utrack_slurm.sh
  9. After completion, merge job package moisture footprints using assemble_footprints.py

## Python Environment

The python environment used for this routine is called utrack_env and can be recreated with the environment.yml file by using the following command:
`conda env create -f environment.yml`

## Input Processing

- **ERA5_water_balance.py** --> script to calculate water balance correction factor alpha
- **ERA5_unit_conversion.py** --> script to convert ERA5 data from m of water equivalent to mm
- **era5_grid2utrack.sh** --> bash script to convert ERA5 data to UTrack format

Filepaths have to be adjusted in these scripts! The water balance calculation script loads filepaths from settings.py of the tracking routine, because it intends to calculate the correction factors based on the exact same evaporation and precipitation inputs that are used in the tracking routine. Please take settings.py file over to this section and adjust manually if necessary.

## Mask Processing

- **utrack_grid.txt** --> contains the grid information for the UTrack climatology; needed to remap data input and mask files
- **shp2attr_raster.py** --> bash script to convert shapefiles to raster files with the same coordinates as the UTrack grid; can be used as a command line tool: `./convert_shapefiles.sh [-a <attribute_or_value>] SHAPEFILE_NAME1 SHAPEFILE_NAME2 ...` but default burn value is 1.
- **mask_screening.py** --> script to screen masks for coordinates and write out coordinates in zone specific csv files

The bash script takes the shapefile of the target zone(s) and converts them to raster files (NetCDF) in UTrack format (specified in utrack_grid.txt). File should be run as command line tool in the folder of the shapefile and shapefile name should be given as argument. The burn value can be specified with the -a flag, otherwise it is set to 1. Alternatively, an attribute from the shapefile can be used as burn value with the -a flag.

The mask screening script takes the raster files and screens them for coordinates. The coordinates are written out in csv files for each zone. Filepaths and burn values/ encoding values have to be adjusted in the script. The script pararellizes the screening process and splits different zones up on separate cores.

## UTrack Database Moisture Tracking

- **utils.py** --> functions to screen masks for coordinates and writing out job packages for core splits, create output directories
- **create_params.py** --> script to create parameter file with job packages
- **settings.py** --> WKDIR and filepaths
- **utrack_functions.py** --> Tracking Functions
- **main.py** --> job runner
- **utrack_slurm.sh** --> send jobs to HPC

- **assemble_runs.py** --> script to merge job packages after completion

### Example start of routine

Activate conda environment containing all necessary modules

`conda activate utrack_env`

Create parameters (don't forget to adjust number of jobs in sbatch job_runner)

`python3 create_params.py`

Test job runner locally

`python3 main.py 1`

Deactivate conda environment

`conda deactivate`

Submit job to slurm

`sbatch utrack_slurm.sh`

After completion, merge job packages
`python3 assemble_runs.py`

### Output

settings.py specifies the output directory for the moisture footprints. The output is in NetCDF format and contains the moisture footprints for each mask in the specified region of interest. The output is in litres per year or litres per month (monthly output).
The delineation of atmospheric watersheds (evaporationsheds and precipitationsheds), analysis on the "most-influential part (MIP)" of the moisture source and sink regions, as well as the calculation of moisture recycling indices can be done with the post-processing scripts (still under development - 18/08/2024).

## Post-Processing

- **atmos_watersheds.py** --> script to delineate atmospheric watersheds from moisture footprints (NetCDF and GeoJSON)
- **settings.py** --> filepaths and settings
