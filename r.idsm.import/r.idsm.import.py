#!/usr/bin/env python3
#
############################################################################
#
# MODULE:      r.idsm.import
# AUTHOR(S):   Lina Krisztian
#
# PURPOSE:     Downloads iDSM (bDOM) for specified federal state and aoi
# COPYRIGHT:   (C) 2025 by mundialis GmbH & Co. KG and the GRASS
#              Development Team
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
############################################################################

# %module
# % description: Downloads iDSM (bDOM) for specified federal state and aoi.
# % keyword: raster
# % keyword: import
# % keyword: DOM
# % keyword: DSM
# % keyword: open-geodata-germany
# %end

# %option G_OPT_V_INPUT
# % key: aoi
# % description: Polygon of the area of interest to set region
# % required: no
# %end

# %option
# % key: federal_state
# % type: string
# % multiple: yes
# % required: no
# % options: Nordrhein-Westfalen,NW
# % description: Federal state(s) related to the area of interest e.g.:"Nordrhein-Westfalen"
# %end

# %option G_OPT_F_INPUT
# % key: federal_state_file
# % description: Path to text file containing the federal state(s) related to the area of interest
# % required: no
# %end

# %option
# % key: download_dir
# % label: Path to output folder
# % description: Path to download folder
# % required: no
# % multiple: no
# %end

# %option G_OPT_R_OUTPUT
# % description: Name for output raster map
# %end

# %flag
# % key: k
# % label: Keep downloaded data in the download directory
# %end

# %flag
# % key: r
# % label: Use native data resolution
# %end

# %rules
# % requires_all: -k,download_dir
# %end

import atexit
import sys

from grass.pygrass.utils import get_lib_path
import grass.script as grass

from grass_gis_helpers.cleanup import general_cleanup
from grass_gis_helpers.open_geodata_germany.download_data import (
    check_download_dir,
)
from grass_gis_helpers.open_geodata_germany.federal_state import (
    get_federal_states,
)
from grass_gis_helpers.raster import create_vrt

# import module library
path = get_lib_path(modname="r.dem.import")
if path is None:
    grass.fatal("Unable to find the dem library directory.")
sys.path.append(path)
try:
    from r_dem_import_lib import OPEN_DATA_AVAILABILITY
except Exception as imp_err:
    grass.fatal(f"r.dem.import library could not be imported: {imp_err}")

# set constant variables
ID = grass.tempname(12)
ORIG_REGION = f"original_region_{ID}"
NOT_YET_SUPPORTED = OPEN_DATA_AVAILABILITY["iDSM"]["NOT_YET_SUPPORTED"]

# set global variables
rm_rasters = []


def cleanup():
    """Cleaning up function"""
    general_cleanup(
        orig_region=ORIG_REGION,
        rm_rasters=rm_rasters,
    )


def main():
    """Main function of r.idsm.import"""
    global rm_rasters

    aoi = options["aoi"]
    federal_states = get_federal_states(
        options["federal_state"], options["federal_state_file"]
    )
    download_dir = check_download_dir(options["download_dir"])
    output = options["output"]
    keep_data = flags["k"]
    native_res = flags["r"]

    # save original region
    grass.run_command("g.region", save=ORIG_REGION, quiet=True)

    # loop over federal states and import data
    all_idsms = []
    for fs in set(federal_states):
        if fs in NOT_YET_SUPPORTED:
            grass.fatal(
                _(
                    "The import of the open data is not yet supported "
                    "or the data are not available as Opendata."
                    f"{fs}."
                )
            )

        # implement data download and import from open data
        r_idsm_import_fs_flags = ""
        if keep_data:
            r_idsm_import_fs_flags += "k"
        if native_res:
            r_idsm_import_fs_flags += "r"
        out_fs = f"idsm_{fs}"
        grass.run_command(
            f"r.idsm.import.{fs.lower()}",
            aoi=aoi,
            download_dir=download_dir,
            output=out_fs,
            flags=r_idsm_import_fs_flags,
            overwrite=True,
        )
        all_idsms.append(out_fs)

    create_vrt(all_idsms, output)
    grass.message(_(f"iDSM raster map <{output}> is created."))


if __name__ == "__main__":
    options, flags = grass.parser()
    atexit.register(cleanup)
    main()
