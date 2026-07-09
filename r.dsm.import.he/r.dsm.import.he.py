#!/usr/bin/env python3
#
############################################################################
#
# MODULE:      r.dsm.import.he
# AUTHOR(S):   Anika Weinmann
# PURPOSE:     Downloads DSM for Hessen and aoi
# SPDX-FileCopyrightText: (c) 2024-2026 by mundialis GmbH & Co. KG and the
#                             GRASS Development Team
# SPDX-License-Identifier: GPL-3.0-or-later.
#
############################################################################

# %module
# % description: Downloads DSM for Hessen and aoi.
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

# %option
# % key: metadata_file
# % type: string
# % required: no
# % description: Temporary file for metadata URLs
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
from datetime import datetime
import os
import pathlib
from time import sleep

from osgeo import gdal
import grass.script as grass

from grass_gis_helpers.cleanup import general_cleanup
from grass_gis_helpers.data_import import (
    download_and_import_tindex,
    get_list_of_tindex_locations,
)
from grass_gis_helpers.open_geodata_germany.download_data import (
    check_download_dir,
)
from grass_gis_helpers.raster import adjust_raster_resolution, create_vrt

# set global variables
TINDEX = (
    "https://github.com/mundialis/tile-indices/raw/main/DSM/HE/"
    "HE_DSM_tindex.gpkg.gz"
)

ID = grass.tempname(12)
RETRIES = 10
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
    """Main function of r.dsm.import.he"""
    global rm_rasters, rm_vectors, keep_data, download_dir

    aoi = options["aoi"]
    download_dir = check_download_dir(options["download_dir"])
    alignment_raster = options["alignment_raster"]
    metadata_file = options["metadata_file"]
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
    tindex_vect = f"dsm_tindex_{ID}"
    rm_vectors.append(tindex_vect)
    download_and_import_tindex(TINDEX, tindex_vect, download_dir)

    # get download urls which overlap with aoi
    url_tiles = get_list_of_tindex_locations(tindex_vect, aoi)

    # import Tif DSM files
    grass.message(_("Importing DSMs..."))
    grass.run_command("g.region", grow=1, quiet=True)
    all_dsms = []
    date_today = datetime.now().strftime("%Y%m%d")
    if native_res:
        dsm_src = gdal.Open(url_tiles[0].replace("DATE", date_today))
        dsm_res = abs(dsm_src.GetGeoTransform()[1])
    for url in url_tiles:
        dsm_name = os.path.splitext(os.path.basename(url))[0].replace("-", "")
        import_kwargs = {
            "input": url.replace("DATE", date_today),
            "output": dsm_name,
            "extent": "region",
            "overwrite": True,
            "quiet": True,
            "memory": 1000,
        }
        if native_res:
            import_kwargs["resolution"] = "value"
            import_kwargs["resolution_value"] = dsm_res
        count = 0
        imported = False
        while not imported and count < RETRIES:
            count += 1
            try:
                grass.run_command("r.import", **import_kwargs)
                imported = True
            except Exception:
                sleep(10)
        all_dsms.append(dsm_name)

    # create VRT
    create_vrt(all_dsms, output)

    # resample / interpolate whole VRT (because interpolating single files leads
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

    if metadata_file and url_tiles:
        try:
            with pathlib.Path(metadata_file).open("w", encoding="utf-8") as f:
                for url in url_tiles:
                    f.write(f"{url.replace('DATE', date_today)}\n")
            grass.debug("Wrote tile URLs to tempfile")
        except Exception as e:
            grass.warning(f"Could not write tempfile metadata: {e}")


if __name__ == "__main__":
    options, flags = grass.parser()
    atexit.register(cleanup)
    main()
