#!/usr/bin/env python3
#
############################################################################
#
# MODULE:      r.idsm.import.bb
# AUTHOR(S):   Veronica Koess, Anika Weinmann
# PURPOSE:     Downloads iDSM for Brandenburg and aoi
# SPDX-FileCopyrightText: (c) 2026 by mundialis GmbH & Co. KG and the
#                             GRASS Development Team
# SPDX-License-Identifier: GPL-3.0-or-later.
#
############################################################################

# %module
# % description: Downloads iDSM for Brandenburg and aoi.
# % keyword: raster
# % keyword: import
# % keyword: DOM
# % keyword: DSM
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

import grass.script as grass
from osgeo import gdal

from grass_gis_helpers.cleanup import general_cleanup
from grass_gis_helpers.data_import import (
    download_and_import_tindex,
    get_list_of_tindex_locations,
)
from grass_gis_helpers.location import (
    create_tmp_location,
    get_current_location,
    switch_back_original_location,
)
from grass_gis_helpers.open_geodata_germany.download_data import (
    check_download_dir,
)
from grass_gis_helpers.raster import create_vrt

# set constant variables
TINDEX = (
    "https://raw.githubusercontent.com/mundialis/tile-indices/main/iDSM/BB/"
    "BB_tileindex_dom_tif_proj.gpkg.gz"
)
EPSGCODE = 25833
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
    """Main function of r.idsm.import.bb"""
    global rm_rasters, rm_vectors, keep_data, download_dir
    # global vars for temporary location
    global gisdbase, tgtgisrc, tmploc, srcgisrc

    aoi = options["aoi"]
    download_dir = check_download_dir(options["download_dir"])
    alignment_raster = options["alignment_raster"]
    output = options["output"]
    keep_data = flags["k"]
    native_res = flags["r"]

    # save original region
    grass.run_command("g.region", save=ORIG_REGION, quiet=True)
    ns_res = grass.region()["nsres"]

    # create region vector if no aoi is given
    if not aoi:
        aoi = f"aoi_region_{ID}"
        rm_vectors.append(aoi)
        grass.run_command("v.in.region", output=aoi)

    # get current resolution
    cur_res = grass.region()["nsres"]

    # set region if aoi is given
    if aoi:
        grass.run_command("g.region", vector=aoi, flags="a")

    # change location to tmp location for data import
    tgtloc, tgtmapset, gisdbase, tgtgisrc = get_current_location()
    tmploc, srcgisrc = create_tmp_location(EPSGCODE)

    # reproject aoi
    if "@" in aoi:
        aoi_name, mapset = aoi.split("@")
    else:
        mapset = tgtmapset
        aoi_name = aoi
    grass.run_command(
        "v.proj",
        location=tgtloc,
        mapset=mapset,
        input=aoi_name,
        output=aoi_name,
        quiet=True,
    )
    grass.run_command("g.region", vector=aoi_name, res=cur_res, flags="a")

    # get tile index
    tindex_vect = f"dsm_tindex_{ID}"
    rm_vectors.append(tindex_vect)
    download_and_import_tindex(TINDEX, tindex_vect, download_dir)

    # get download urls which overlap with aoi
    url_tiles = get_list_of_tindex_locations(tindex_vect, aoi)

    # import iDSMs directly
    grass.message(_(f"Importing {len(url_tiles)} iDSMs..."))
    all_dsms = []
    if native_res:
        dsm_src = gdal.Open(url_tiles[0])
        dsm_res = abs(dsm_src.GetGeoTransform()[1])
    for url in url_tiles:
        dsm_name = os.path.splitext(os.path.basename(url))[0].replace("-", "")
        if "/vsicurl/" not in url:
            url = f"/vsicurl/{url}"
        # Currently bDOM tifs are given with COMPOUNDCRS
        # with PROJCRS: 25833 and VERTCRS: 7837 (for vertical data)
        # r.import check of CRS yields error, even in 25833 projection.
        # Thus for now ignore projection check and expect 25833
        # TODO/NOTE: remove -o flag when handled from r.import or
        # CRS of original bDOM data change
        grass.warning(
            _("Importing data with -o flag, because of COMPOUNDCRS.")
        )
        import_kwargs = {
            "input": url,
            "output": dsm_name,
            "extent": "region",
            "overwrite": True,
            "quiet": True,
            "memory": 1000,
            "flags": "o",
        }
        if native_res:
            import_kwargs["resolution"] = "value"
            import_kwargs["resolution_value"] = dsm_res
        grass.run_command("r.import", **import_kwargs)
        all_dsms.append(dsm_name)

    # create VRT
    create_vrt(all_dsms, output)

    # get native data resolution
    if native_res:
        res = float(
            grass.parse_command("r.info", map=output, flags="g")["nsres"]
        )
    # switch back to origin location
    switch_back_original_location(tgtgisrc)

    if not native_res:
        res = ns_res
    if alignment_raster:
        grass.run_command("g.region", vector=aoi, align=alignment_raster)
    else:
        grass.run_command("g.region", vector=aoi, res=res, flags="a")
    grass.run_command(
        "r.proj",
        location=tmploc,
        mapset="PERMANENT",
        input=output,
        output=output,
        method="bilinear",
        flags="n",
        quiet=True,
        memory=1000,
    )

    grass.message(_(f"iDSM raster map <{output}> is created."))


if __name__ == "__main__":
    options, flags = grass.parser()
    atexit.register(cleanup)
    main()
