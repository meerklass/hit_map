"""Run hit_map.py in parallel on an HPC via slurm given a list of block numbers."""
import os
import click
from pathlib import Path

import numpy as np

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"], "max_content_width": 100}

BASE_DIR = Path("__file__").parent


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "-f",
    "--block-number-file",
    required=True,
    type=click.Path(exists=True),
    help="A text file containing a list of block numbers, one per line",
)
@click.option(
    "-n",
    "--nside",
    type=int,
    default=64,
    show_default=True,
    help="NSIDE of the HEALPix hit map",
)
def main(block_number_file, nside):
    """Run hit_map.py in parallel on an HPC via slurm given a list of block numbers."""

    block_numbers = np.loadtxt(block_number_file, dtype=int)

    logdir = BASE_DIR / "logs"
    if not logdir.exists():
        logdir.mkdir(parents=True)

    for bn in block_numbers:
        program = f"""#!/bin/bash
#SBATCH -o logs/hit_map_{bn}-%j.out
#SBATCH --job-name=hit_map_{bn}
#SBATCH --mem=64GB
#SBATCH --partition=Main
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:10:00

source ~/miniconda3/bin/activate
conda activate meerklass

python hit_map.py -b {bn} -n {nside}
"""
        with open("_hit_map.sbatch", "w") as fl:
            fl.write(program)

        os.system("sbatch _hit_map.sbatch")


if __name__ == "__main__":
    main()
