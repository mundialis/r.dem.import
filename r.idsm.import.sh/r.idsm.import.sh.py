#!/usr/bin/env python3
#
############################################################################
#
# MODULE:      r.idsm.import.sh
# AUTHOR(S):   Kim Kaiser, Veronica Koess, Anika Weinmann
# PURPOSE:     Downloads iDSM for Schleswig-Holstein
# SPDX-FileCopyrightText: (c) 2026 by mundialis GmbH & Co. KG and the
#                             GRASS Development Team
# SPDX-License-Identifier: GPL-3.0-or-later.
#
############################################################################

# %module
# % description: Downloads iDSM for Schleswig-Holstein and aoi.
# % keyword: raster
# % keyword: import
# % keyword: DOM
# % keyword: DSM
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

# %option G_OPT_R_INPUT
# % key: alignment_raster
# % required: no
# % description: Name of raster map, used for raster alignment (if not given, dem extent and region resolution is used)
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
# % excludes: -r,alignment_raster
# %end

import atexit
import os
from urllib.parse import urlparse, parse_qs
import grass.script as grass

from grass_gis_helpers.cleanup import general_cleanup
from grass_gis_helpers.data_import import download_and_import_tindex
from grass_gis_helpers.open_geodata_germany.download_data import (
    check_download_dir,
)
from grass_gis_helpers.raster import adjust_raster_resolution, create_vrt

# set variables
TINDEX = (
    "https://github.com/kimariak/tile-indices/raw/sh_tindex/iDSM/SH/"
    "sh_bdom_tindex_proj.gpkg.gz"
)
CURRENT_WORKING_DIR = os.getcwd()
ID = grass.tempname(12)
ORIG_REGION = f"original_region_{ID}"

keep_data = False
download_dir = None
rm_rasters = []
rm_vectors = []


def cleanup():
    """Cleaning up function"""
    os.chdir(CURRENT_WORKING_DIR)
    rm_dirs = []
    if not keep_data:
        if download_dir:
            rm_dirs.append(download_dir)
    general_cleanup(
        orig_region=ORIG_REGION,
        rm_rasters=rm_rasters,
        rm_vectors=rm_vectors,
        rm_dirs=rm_dirs,
        rm_mask=True,
    )


def main():
    """Main function of r.idsm.import.sh"""
    global rm_rasters, rm_vectors, keep_data, download_dir

    aoi = options["aoi"]
    download_dir = check_download_dir(options["download_dir"])
    alignment_raster = options["alignment_raster"]
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

    # get tiles which overlap with aoi
    def url_tiles(tindex_vect, aoi):
        tindex_clipped = f"clipped_tindex_vect_{grass.tempname(8)}"
        try:
            v_clip_kwargs = {
                "input": tindex_vect,
                "output": tindex_clipped,
                "flags": "",
                "quiet": True,
            }
            if aoi:
                v_clip_kwargs["clip"] = aoi
                v_clip_kwargs["flags"] += "d"
            else:
                v_clip_kwargs["flags"] += "r"
            grass.run_command("v.clip", **v_clip_kwargs)
            tiles = [
                val[0]
                for val in grass.vector_db_select(
                    tindex_clipped,
                    columns="link_data",
                )["values"].values()
            ]

            return tiles

        finally:
            rm_vectors.extend(tindex_clipped)

    # create list with tile urls
    url_tiles_list = url_tiles(tindex_vect, aoi)

    # import iDSM files
    grass.message(_("Importing iDSM..."))
    all_idsms = []
    for url in url_tiles_list:
        if aoi:
            grass.run_command("g.region", vector=aoi)
        else:
            grass.run_command("g.region", region=ORIG_REGION)
        grass.run_command("g.region", res=1, grow=1, quiet=True)
        idsm_name = os.path.splitext(parse_qs(urlparse(url).query)["file"][0])[
            0
        ]
        grass.run_command(
            "r.import",
            input=url,
            output=idsm_name,
            extent="region",
            overwrite=True,
            quiet=True,
        )
        all_idsms.append(idsm_name)

    # create VRT
    tmp_out = f"tmp_{output}_{ID}"
    rm_rasters.append(tmp_out)
    rm_rasters.extend(all_idsms)
    create_vrt(all_idsms, tmp_out)

    # clip to region / aoi
    if aoi:
        grass.run_command("g.region", vector=aoi, align=tmp_out)
    else:
        grass.run_command("g.region", region=ORIG_REGION, align=tmp_out)
    grass.run_command(
        "r.mapcalc", expression="MASK = 1", overwrite=True, quiet=True
    )
    grass.run_command(
        "r.mapcalc",
        expression=f"{output} = {tmp_out}",
        quiet=True,
    )

    # resample/interpolate whole VRT (because interpolating single files leads
    # to empty rows and columns)
    # check resolution and resample / interpolate data if needed
    if not native_res:
        if alignment_raster:
            # set extent from imported data, and align with alignment raster
            grass.run_command(
                "g.region", raster=output, align=alignment_raster
            )
            ns_res = float(
                grass.parse_command("r.info", map=alignment_raster, flags="g")[
                    "nsres"
                ],
            )
        else:
            # if no alignemnt raster is given,
            # use extent of imported data and
            # set and align with current region resolution
            grass.run_command("g.region", raster=output)
            grass.run_command("g.region", res=ns_res, flags="a")
        grass.message(_("Resampling / interpolating data..."))
        grass.run_command("g.rename", raster=f"{output},{output}_tmp")
        adjust_raster_resolution(f"{output}_tmp", output, ns_res)
        rm_rasters.append(f"{output}_tmp")

    grass.message(_(f"DSM raster map <{output}> is created."))


if __name__ == "__main__":
    options, flags = grass.parser()
    atexit.register(cleanup)
    main()
