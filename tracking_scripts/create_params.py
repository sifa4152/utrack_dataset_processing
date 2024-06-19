# -*- coding: utf-8 -*-
# create_params.py --> runner for creating parameter files for the tracking algorithm (job splitting)
import glob
import os
import sys
import settings
from utils import params_creator


if __name__ == '__main__':
    files = glob.glob(os.path.join(settings.PATH_TARGET_ZONES, 'target_cells_*.csv')) # target cell coordinates (lat,lon)
    params_creator(files, STEP_SIZE=200)
