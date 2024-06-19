#!/bin/bash

# ALTERNATIVE APPROACH = MULTIPLYING BW_FP BY PRECIP AND CONVERTING TO LITRES!
# UTrack runs on HPC: --> run main.py script with a job array

#SBATCH --job-name=utrack                                                     
#SBATCH --account=open                                                          
#SBATCH --partition=standard                                                     
#SBATCH --qos=short                                                                     # short:24h; medium:7d; long:30d
#SBATCH --array=1-300                                                                   # how many tasks in the array (num of job packages)
#SBATCH --cpus-per-task=1                                                               # one CPU core per task
#SBATCH --output=hpc_out/utrack-%j-%a.out                                        
#SBATCH --error=hpc_out/utrack-%j-%a.err                                        
#SBATCH --workdir=/path/to/directory/with/tracking/scripts
#SBATCH --mail-type=ALL                                                         
#SBATCH --mail-user=hpc.user@email.com                           


# Load software
module load anaconda/2021.11c          # load anaconda module                                                    
source activate utrack_env             # load python environment                                         


# Run python script with a command line argument
srun python main.py $SLURM_ARRAY_TASK_ID                                      
