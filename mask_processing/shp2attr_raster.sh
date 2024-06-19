#!/bin/bash
# Script to convert basin shapefiles to mask arrays and regrid to a specified format
# Requires GDAL and CDO to be installed
# State: 18-06-2024, simonfa
# Usage: ./convert_shapefiles.sh [-a <attribute_or_value>] SHAPEFILE_NAME1 SHAPEFILE_NAME2 ...

# Check if required tools are installed
command -v gdal_rasterize >/dev/null 2>&1 || { echo >&2 "gdal_rasterize is required but not installed. Aborting."; exit 1; }
command -v gdal_translate >/dev/null 2>&1 || { echo >&2 "gdal_translate is required but not installed. Aborting."; exit 1; }
command -v cdo >/dev/null 2>&1 || { echo >&2 "cdo is required but not installed. Aborting."; exit 1; }

# Default values
resolution="0.5" # Resolution of the output grid
bbox="-180 -90 180 90" # Bounding box of the output grid
grid_file="utrack_grid.txt" # File containing the target grid information
attribute_or_value="1"  # Default burn value if -a is not specified

# Function to display usage instructions
function show_usage() {
  echo "Usage: $0 [-a <attribute_or_value>] SHAPEFILE_NAME1 SHAPEFILE_NAME2 ..."
  echo "Options:"
  echo "  -a  Attribute name for burn value or a fixed numeric burn value (default is 1)"
  exit 1
}

# Parse command line options
while getopts "a:" opt; do
  case $opt in
    a) attribute_or_value="$OPTARG" ;;
    *) show_usage ;;
  esac
done

# Shift arguments so only shapefile names remain
shift $((OPTIND -1))

# Check if the grid file exists
if [[ ! -f $grid_file ]]; then
  echo "Grid file $grid_file not found. Please provide a valid grid file."
  exit 1
fi

# Iterate over the provided shapefiles
for shapefile in "$@"; do
  # Verify that the input file exists with the .shp extension
  if [[ ! -f "${shapefile}.shp" ]]; then
    echo "Shapefile ${shapefile}.shp not found. Skipping..."
    continue
  fi

  # Define output filenames based on the shapefile name
  tiff_file="${shapefile}.tiff"
  nc_file="${shapefile}.nc"
  remap_nc_file="remap_${shapefile}.nc"

  echo "Processing $shapefile..."

  # Determine if the attribute_or_value is a number (fixed value) or a string (attribute name)
  if [[ $attribute_or_value =~ ^[0-9]+$ ]]; then
    # Fixed burn value
    gdal_rasterize -ot UInt16 -burn $attribute_or_value -te $bbox -tr $resolution $resolution -l $shapefile "${shapefile}.shp" $tiff_file
  else
    # Attribute-based burn value
    gdal_rasterize -ot UInt16 -at -a $attribute_or_value -te $bbox -tr $resolution $resolution -l $shapefile "${shapefile}.shp" $tiff_file
  fi

  if [ $? -ne 0 ]; then
    echo "Error rasterizing ${shapefile}.shp. Skipping..."
    continue
  fi

  # Convert the TIFF file to a NetCDF file
  gdal_translate -of NetCDF $tiff_file $nc_file
  if [ $? -ne 0 ]; then
    echo "Error converting $tiff_file to NetCDF. Skipping..."
    continue
  fi

  # Remap the NetCDF file to the target grid
  cdo remapnn,$grid_file $nc_file $remap_nc_file
  if [ $? -ne 0 ]; then
    echo "Error remapping $nc_file. Skipping..."
    continue
  fi

  echo "Output saved to $remap_nc_file"

  # Clean up intermediate files
  rm -f $tiff_file $nc_file

done

echo "Processing completed."
