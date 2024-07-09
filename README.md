# MeerKLASS Hit Map

Make hit maps. Currently, UHF only.

## How to update

0. `environment.yaml` can be used to set up a neccesary Python environment, e.g. `conda env create -f environment.yaml`
1. Make file containing a list of good blocks, or update existing files in the directory, i.e. `uhf_all_good_blocks.txt`
2. Do `python run_hit_map_slrum.py -f uhf_all_good_blocks.txt`. This will submit a bunch of SLURM jobs. Each job will make a hit map for each block number, saving the it to `/idia/projects/hi_im/uhf_hit_maps`. The default NSIDE is 64, corresponding to angular resolution of ~1 degree.
3. Execute the `hit_map.ipynb` notebook. This will combine the hit maps from all blocks into a single map and plot it.
