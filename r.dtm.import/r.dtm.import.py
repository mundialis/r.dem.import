#!/usr/bin/env python3
#
############################################################################
#
# MODULE:      r.dtm.import
# AUTHOR(S):   Anika Weinmann
#
# PURPOSE:     Downloads DTM for specified federal state and aoi
# COPYRIGHT:   (C) 2024 by mundialis GmbH & Co. KG and the GRASS
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
# % description: Downloads and imports DTM for specified federal state and aoi.
# % keyword: raster
# % keyword: import
# % keyword: DGM
# % keyword: DTM
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
# % options: Berlin,BE,Baden-Württemberg,Brandenburg,BB,BW,Bayern,BY,Hamburg,HH,Hessen,HE,Sachsen,SN,Thüringen,TH
# % description: Federal state(s) related to the area of interest e.g.:"Nordrhein-Westfalen"
# %end

# %option G_OPT_F_INPUT
# % key: federal_state_file
# % description: Path to text file containing the federal state(s) related to the area of interest
# % required: no
# %end

# %option G_OPT_M_DIR
# % key: local_data_dir
# % required: no
# % description: Directory with raster map of DTMs to import (e.g. XYZ/TXT files)
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
import os
import sys

import grass.script as grass
from grass.pygrass.utils import get_lib_path

from grass_gis_helpers.cleanup import general_cleanup
from grass_gis_helpers.data_import import import_local_xyz_files
from grass_gis_helpers.open_geodata_germany.download_data import (
    check_download_dir,
)
from grass_gis_helpers.open_geodata_germany.federal_state import (
    get_federal_states,
)
from grass_gis_helpers.raster import adjust_raster_resolution, create_vrt

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
NO_OPEN_DATA = OPEN_DATA_AVAILABILITY["DTM"]["NO_OPEN_DATA"]
NOT_YET_SUPPORTED = OPEN_DATA_AVAILABILITY["DTM"]["NOT_YET_SUPPORTED"]
# set global variables
rm_rasters = []


def cleanup():
    """Cleaning up function"""
    general_cleanup(
        orig_region=ORIG_REGION,
        rm_rasters=rm_rasters,
    )


def import_local_data(aoi, out, local_data_dir, fs, all_dtms):
    """Import local DTM data

    Args:
        aoi (str): Vector map with area of interest
        out (str): Base output name
        local_data_dir (str): Path to local data directory with federal state
                              subfolders
        fs (str): the abbrivation of the federal state
        all_dtms (list): empty list where the imported DTM rasters
                         will be appended
    """
    imported_local_data = import_local_xyz_files(
        aoi,
        f"{out}_{fs}",
        os.path.join(local_data_dir, fs),
        all_dtms,
    )

    if not imported_local_data and fs in ["BW"]:
        grass.fatal(_("Local data does not overlap with aoi."))
    elif not imported_local_data:
        grass.message(
            _(
                "Local data does not overlap with aoi. Data will be downloaded"
                " from Open Data portal."
            )
        )
    return imported_local_data


def main():
    """Main function of r.dtm.import"""
    global rm_rasters

    aoi = options["aoi"]
    federal_states = get_federal_states(
        options["federal_state"], options["federal_state_file"]
    )
    local_data_dir = options["local_data_dir"]
    download_dir = check_download_dir(options["download_dir"])
    output = options["output"]
    keep_data = flags["k"]
    native_res = flags["r"]

    # save original region
    grass.run_command("g.region", save=ORIG_REGION, quiet=True)
    ns_res = grass.region()["nsres"]

    # local DTM files
    local_fs_list = []
    if local_data_dir and local_data_dir != "":
        local_fs_list = os.listdir(local_data_dir)

    # loop over federal states and import data
    all_dtms = []
    for fs in set(federal_states):
        # check if local data for federal state given
        imported_local_data = False
        if fs in local_fs_list:
            imported_local_data = import_local_data(
                aoi, output, local_data_dir, fs, all_dtms
            )
        elif fs in NO_OPEN_DATA:
            grass.fatal(
                _(
                    f"No local data for {fs} available. For the federal state "
                    "there are no open data available. Is the path correct?"
                )
            )

        # import data when local import was not used
        if not imported_local_data:
            if fs in NOT_YET_SUPPORTED:
                grass.fatal(
                    _(
                        "The import of the open data is not yet supported for "
                        f"{fs}."
                    )
                )
            elif fs in NO_OPEN_DATA:
                grass.fatal(
                    _(
                        f"For the federal state {fs} there are no open data "
                        "available. Please use local data <local_data_dir>."
                    )
                )
            # implement data download and import from open data
            r_dtm_import_fs_flags = ""
            if keep_data:
                r_dtm_import_fs_flags += "k"
            if native_res:
                r_dtm_import_fs_flags += "r"
            out_fs = f"dtm_{fs}"
            grass.run_command(
                f"r.dtm.import.{fs.lower()}",
                aoi=aoi,
                download_dir=download_dir,
                output=out_fs,
                flags=r_dtm_import_fs_flags,
                overwrite=True,
            )
            all_dtms.append(out_fs)

    create_vrt(all_dtms, output)

    # resample / interpolate whole VRT (because interpolating single files leads
    # to empty rows and columns)
    # check resolution and resample / interpolate data if needed
    if not native_res:
        grass.run_command("g.region", raster=output, res=ns_res)
        grass.message(_("Resampling / interpolating data..."))
        adjust_raster_resolution(output, output, ns_res)

    grass.message(_(f"DTM raster map <{output}> is created."))


if __name__ == "__main__":
    options, flags = grass.parser()
    atexit.register(cleanup)
    main()
