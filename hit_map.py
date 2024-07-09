#!/usr/bin/env python3
"""Calculate hit count giving a block number."""
import logging
from pathlib import Path
import pickle

import click
import numpy as np
import healpy as hp

from museek.enums.result_enum import ResultEnum


CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"], "max_content_width": 100}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


BASE_DIR = Path("/idia/projects/hi_im")


def get_radec(data_file):
    """Read pointing positions (RA, Dec) from a MeerKLASS museek
    `scan_track_split_plugin.pickle` file."""
    logger.info(f"Reading pointing infomation from {data_file}")

    with open(data_file, "rb") as df:
        data = pickle.load(df)
    scan_data = data.get(ResultEnum.SCAN_DATA).result
    antenna_list = scan_data._antenna_name_list
    ra = scan_data.right_ascension.array[:, 0, antenna_list.index("m001")]
    dec = scan_data.declination.array[:, 0, antenna_list.index("m001")]
    return ra, dec


def radec_to_hit_map(ra: np.ndarray, dec: np.ndarray, nside: int = 64) -> np.ndarray:
    """Convert RA-Dec positions into counts on a healpix grid at specific NSIDE.

    Parameters:
    ra: np.ndarray
        Right ascensions in degree, range = [0, 360]
    dec: np.ndarray
        Declination in degree, range = [-90, +90]
    nsidel: int
        Healpix NSIDE, optional
        Default NSIDE=64 is about 1 deg resolution, which is what we care for cosmology.

    Returns:
    indices, counts:
        Tuble of healpix pixel indices and their counts
    """
    logger.info(f"Calculating number of hits on a HEALPix grid with NSIDE={nside}")

    # Convert to theta, phi (colatitude, longitude)
    theta = np.deg2rad(90 - dec)
    phi = np.deg2rad(ra)

    # Convert to HEALPix indices and do the count
    hpx_indices = hp.ang2pix(nside, theta, phi)
    unique_indices, counts = np.unique(hpx_indices, return_counts=True)

    # Make a map from counts
    hmap = np.zeros(hp.nside2npix(nside))
    hmap[unique_indices] = counts

    return hmap


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "-b",
    "--block-number",
    type=int,
    help="Observation block number (UHF only)",
)
@click.option(
    "-n",
    "--nside",
    type=int,
    default=64,
    show_default=True,
    help="NSIDE of the HEALPix hit map",
)
def hit_map(block_number: int, nside: int = 64):
    """Make a HEALPIx hit map given a block number.

    The script will search for `scan_track_split_plugin.pickle` given a block number,
    extract pointing positions (RA, Dec), and count the number of hits at each HEALPix
    pixel.

    Output is saved into a file named "hit_map_healpix_nside{nside}_{block_number}.npy"
    in a directoty "/idia/projects/hi_im/uhf_hit_maps" as a record array with
    two columns, "indices" and "hits".

    Currently, only work for UHF data
    """

    # Search for `scan_track_split_plugin.pickle`. This file can either be in
    # "pipeline", "pipeline_results", or "sanity_check" sub directories.
    # They are all the same, so we just grab one of them
    data_file = sorted(
        BASE_DIR.glob(f"uhf_*/**/{block_number}/scan_track_split_plugin.pickle")
    )[0]

    ra, dec = get_radec(data_file)

    hmap = radec_to_hit_map(ra, dec)
    # hpx_indices, counts = radec_to_hit_map(ra, dec, nside)
    # out_array = np.rec.fromarrays([hpx_indices, counts], names="indices,hits")

    outdir = BASE_DIR / "uhf_hit_maps"
    if not outdir.exists():
        outdir.mkdir(parents=True)

    outfile = outdir / f"hit_map_healpix_nside{nside}_{block_number}.npy"
    logger.info(f"Saving results to: {outfile}")
    np.save(outfile, hmap)

    logger.info("Done!")


if __name__ == "__main__":
    hit_map()
