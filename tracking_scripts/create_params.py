# -*- coding: utf-8 -*-
# create_params.py --> runner for creating parameter files for the tracking algorithm (job splitting)
import glob
import os
import sys
import settings
from utils import params_creator

# sys.path.insert(1,'/p/projects/open/simon/bgwater/GCEW/final_report/NL_BE_case_study/2024_05_08_NL_BE_runs')
# from importlib import reload # reload 
# reload(settings)


if __name__ == '__main__':
    files = glob.glob(os.path.join(settings.PATH_TARGET_ZONES, 'target_cells_*.csv')) # target cell coordinates (lat,lon)
    params_creator(files, STEP_SIZE=200)