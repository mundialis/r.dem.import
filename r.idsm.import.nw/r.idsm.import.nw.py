#!/usr/bin/env python3
#
############################################################################
#
# MODULE:      r.idsm.import.nw
# AUTHOR(S):   Lina Krisztian
#
# PURPOSE:     Downloads iDSM for Nordrhein-Westfalen and aoi
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
# % description: Downloads iDSM for Nordrhein-Westfalen and aoi.
# % keyword: raster
# % keyword: import
# % keyword: bDOM
# % keyword: iDSM
# % keyword: open-geodata-germany
# %end

# %option G_OPT_V_INPUT
# % key: aoi
# % description: Polygon of the area of interest to set region
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
import os
import grass.script as grass

from grass_gis_helpers.cleanup import general_cleanup
from grass_gis_helpers.data_import import (
    download_and_import_tindex,
    get_list_of_tindex_locations,
)
from grass_gis_helpers.open_geodata_germany.download_data import (
    check_download_dir,
    download_data_using_threadpool,
)
from grass_gis_helpers.raster import adjust_raster_resolution, create_vrt

# set constant variables
TINDEX = (
    "https://github.com/mundialis/tile-indices/raw/main/iDSM/NW/"
    "nw_idsm_tindex_proj.gpkg.gz"
)
RESOLUTION = 0.5

ID = grass.tempname(12)
ORIG_REGION = f"original_region_{ID}"

# set global variables
keep_data = False
download_dir = None
rm_rasters = []
rm_vectors = []


def cleanup():
    """Cleaning up function"""
    rm_dirs = []
    if not keep_data:
        if download_dir:
            rm_dirs.append(download_dir)
    general_cleanup(
        orig_region=ORIG_REGION,
        rm_rasters=rm_rasters,
        rm_vectors=rm_vectors,
        rm_dirs=rm_dirs,
    )


def main():
    """Main function of r.idsm.import.nw"""
    global keep_data, download_dir

    aoi = options["aoi"]
    download_dir = check_download_dir(options["download_dir"])
    output = options["output"]
    keep_data = flags["k"]
    native_res = flags["r"]

    # save original region
    grass.run_command("g.region", save=ORIG_REGION, quiet=True)
    ns_res = grass.region()["nsres"]

    # set region if aoi is given
    if aoi:
        grass.run_command("g.region", vector=aoi, flags="a")

    # get tile index
    tindex_vect = f"idsm_tindex_{ID}"
    rm_vectors.append(tindex_vect)
    download_and_import_tindex(TINDEX, tindex_vect, download_dir)

    # get download urls which overlap with aoi
    url_tiles = get_list_of_tindex_locations(tindex_vect, aoi)

    # Download iDSMS
    grass.message(_("Downloading iDSMs..."))
    download_data_using_threadpool(url_tiles, download_dir, 3)

    # Import iDSMS
    grass.message(_("Importing iDSMs..."))
    all_idsms = []
    for url in url_tiles:
        idsm_name = os.path.splitext(os.path.basename(url))[0].replace("-", "")
        r_in_pdal_kwargs = {
            "input": os.path.join(download_dir, f"{idsm_name}.laz"),
            "output": idsm_name,
            "resolution": RESOLUTION,
            "type": "FCELL",
            "method": "percentile",
            "pth": 95,
            "quiet": True,
            "overwrite": True,
            "flags": "og",
        }
        reg_extent_laz = grass.parse_command(
            "r.in.pdal",
            **r_in_pdal_kwargs,
        )
        reg_laz_split = reg_extent_laz["n"].split(" ")
        grass.run_command(
            "g.region",
            n=float(reg_laz_split[0]),
            s=float(reg_laz_split[1].replace("s=", "")),
            e=float(reg_laz_split[2].replace("e=", "")),
            w=float(reg_laz_split[3].replace("w=", "")),
            res=1,
            flags="a",
        )
        grass.run_command(
            "g.region",
            res=RESOLUTION,
        )
        # # for no missing values at the border of the whole area we grow it
        # grass.run_command("g.region", grow=5)
        r_in_pdal_kwargs["flags"] = "o"
        grass.run_command("r.in.pdal", **r_in_pdal_kwargs)
        all_idsms.append(idsm_name)

    # resample / interpolate whole VRT (because interpolating single files leads
    # to empty rows and columns)
    # check resolution and resample / interpolate data if needed
    if not native_res:
        # create VRT
        vrt = f"vrt_idsm_{ID}"
        rm_rasters.append(vrt)
        create_vrt(all_idsms, vrt)

        grass.message(_("Resampling / interpolating data..."))
        grass.run_command("g.region", raster=vrt, res=ns_res, flags="a")
        adjust_raster_resolution(vrt, output, ns_res)
        rm_rasters.extend(all_idsms)
    else:
        # create VRT
        create_vrt(all_idsms, output)

    grass.message(_(f"iDSM raster map <{output}> is created."))


if __name__ == "__main__":
    options, flags = grass.parser()
    atexit.register(cleanup)
    main()
