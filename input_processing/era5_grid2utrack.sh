#!/bin/bash
# Script to remap ERA5 data to UTrack grid using CDO
# Usage: ./remap_era5.sh

# Check if required tools are installed
command -v cdo >/dev/null 2>&1 || { echo >&2 "cdo is required but not installed. Aborting."; exit 1; }

# Array of ERA5 files to remap
declare -a era5_files=('era5_monthly_tp_1979_2021_mm_month.nc' 'era5_monthly_e_1979_2021_mm_month.nc')

# Target grid file
grid_file="utrack_grid.txt"

# Function to display usage instructions
function show_usage() {
  echo "Usage: $0"
  exit 1
}

# Check if the grid file exists
if [[ ! -f $grid_file ]]; then
  echo "Grid file $grid_file not found. Please provide a valid grid file."
  exit 1
fi

# Loop through each ERA5 file and remap to the UTrack grid
for file in "${era5_files[@]}"; do
  output_file="remap_$file"
  
  echo "Remapping $file to UTrack grid..."

  # Remap using CDO
  cdo remapnn,$grid_file $file $output_file

  if [ $? -ne 0 ]; then
    echo "Error remapping $file. Skipping..."
    continue
  fi

  echo "Remapping completed. Output saved to $output_file"
done

echo "All files remapped successfully."
