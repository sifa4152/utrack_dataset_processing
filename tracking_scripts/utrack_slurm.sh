#!/bin/bash

# ALTERNATIVE APPROACH = MULTIPLYING BW_FP BY PRECIP AND CONVERTING TO LITRES!
# UTrack runs on HPC: --> run main.py script with a job array

#SBATCH --job-name=utrack                                                     
#SBATCH --account=open                                                          
#SBATCH --partition=standard                                                     
#SBATCH --qos=short                                                                     # short:24h; medium:7d; long:30d
#SBATCH --array=1-3                                                                  # how many tasks in the array
#SBATCH --cpus-per-task=1                                                               # one CPU core per task
#SBATCH --output=hpc_out/utrack-%j-%a.out                                        
#SBATCH --error=hpc_out/utrack-%j-%a.err                                        
#SBATCH --workdir=/p/projects/open/simon/bgwater/GCEW/final_report/NL_BE_case_study/2024_05_08_NL_BE_runs 
#SBATCH --mail-type=ALL                                                         
#SBATCH --mail-user=simon.fahrlaender@pik-potsdam.de                            


# Load software
module load anaconda/2021.11c                                                    
source activate utrack_env                                                      

# alias python='/p/projects/open/simon/envs/utrack_env/bin/python3.9'
# . ~/.bashrc

# Run python script with a command line argument
srun python main.py $SLURM_ARRAY_TASK_ID                                      
