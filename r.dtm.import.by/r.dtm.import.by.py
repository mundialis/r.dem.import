#!/usr/bin/env python3
#
############################################################################
#
# MODULE:      r.dtm.import.by
# AUTHOR(S):   Kim Kaiser
# PURPOSE:     Downloads DTM for Bayern
# SPDX-FileCopyrightText: (c) 2026 by mundialis GmbH & Co. KG and the
#                             GRASS Development Team
# SPDX-License-Identifier: GPL-3.0-or-later.
#
############################################################################

# %module
# % description: Downloads DTM for Bayern and aoi.
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
import os
import pathlib
import sys

import grass.script as grass
import requests
from grass.pygrass.utils import get_lib_path
from grass_gis_helpers.cleanup import general_cleanup
from grass_gis_helpers.open_geodata_germany.download_data import (
    check_download_dir,
)
from grass_gis_helpers.raster import (
    adjust_raster_resolution,
    create_vrt,
    vrt_to_raster,
)
from parsel import Selector

# import module library
path = get_lib_path(modname="r.dem.import")
if path is None:
    grass.fatal("Unable to find the dem library directory.")
sys.path.append(path)
try:
    from r_dem_import_lib import create_grid_and_tiles_list
except Exception as imp_err:
    grass.fatal(f"r.dem.import library could not be imported: {imp_err}")

# set variables
URL = "https://services.atlas.bayern.de/getFeature/url"
# WMS with tile url information used as external tindex
TINDEX_WMS = "https://geoservices.bayern.de/od/wms/grid/v1/opendatagrid||dgm1||Opendata_Auswahl_DGM1"
NATIVE_DTM_RES = 1
ID = grass.tempname(12)
ORIG_REGION = f"original_region_{ID}"

keep_data = False
download_dir = None
rm_rasters = []
rm_vectors = []
rm_dirs = []


def cleanup():
    """Cleaning up function."""
    rm_dirs = []
    if not keep_data and download_dir:
        rm_dirs.append(download_dir)
    general_cleanup(
        orig_region=ORIG_REGION,
        rm_rasters=rm_rasters,
        rm_vectors=rm_vectors,
        rm_dirs=rm_dirs,
        rm_mask=True,
    )


def main():
    """Main function of r.dtm.import.by."""
    global download_dir, rm_vectors

    aoi = options["aoi"]
    download_dir = check_download_dir(options["download_dir"])
    alignment_raster = options["alignment_raster"]
    metadata_file = options["metadata_file"]
    output = options["output"]
    fs = "BY"
    native_res = flags["r"]

    # save original region
    grass.run_command("g.region", save=ORIG_REGION, quiet=True)

    # get region resolution and check if resolution consistent
    reg = grass.region()
    if reg["nsres"] == reg["ewres"]:
        ns_res = reg["nsres"]
    else:
        grass.fatal("N/S resolution is not the same as E/W resolution!")

    # set region if aoi is given
    if aoi:
        # pylint: disable=E0601
        grass.run_command("g.region", vector=aoi, res=ns_res, flags="a")
    # if no aoi save region as aoi
    else:
        aoi = f"region_aoi_{ID}"
        grass.run_command(
            "v.in.region",
            output=aoi,
            quiet=True,
        )

    # get size of aoi from region extent
    aoi_ext = grass.region()
    ns_size = aoi_ext["n"] - aoi_ext["s"]
    ew_size = aoi_ext["e"] - aoi_ext["w"]

    # create grid for downloading
    grass.message(_("Creating DTM tiles for BY..."))

    # set tile size in map units (meter)
    tile_size = 1000

    # set grid name
    grid = f"tmp_grid_ST_{ID}"

    # create grid with lib function
    rm_vectors, number_tiles, tiles_list = create_grid_and_tiles_list(
        ns_size,
        ew_size,
        tile_size,
        grid,
        rm_vectors,
        aoi,
        ID,
        fs,
    )

    # extract center coordinates from tiles
    query_points = []
    for tile in tiles_list:
        coords = grass.read_command(
            "v.out.ascii",
            input=tile,
            type="centroid",
            format="point",
            separator="comma",
            quiet=True,
        )
        x, y = map(float, coords.strip().split(",")[:2])
        query_points.append((x, y))

    # get download URLs from WMS (external Tindex)
    url_list = []
    for x, y in query_points:
        payload = {
            "urlOrId": TINDEX_WMS,
            "easting": x,
            "northing": y,
            "srid": 25832,
            "resolution": NATIVE_DTM_RES,
        }
        response = requests.post(URL, json=payload, timeout=30)
        response.raise_for_status()
        selector = Selector(text=response.json()["content"])
        downloadlink = selector.css("a::attr(href)").get()
        if downloadlink:
            url_list.append(downloadlink)
        else:
            continue

    # import DTMs
    grass.message(_(f"Importing {number_tiles} DTMs..."))
    all_dtms = []
    for url in url_list:
        dtm_name = os.path.splitext(pathlib.Path(url).name)[0]
        grass.run_command(
            "r.import",
            input=url,
            output=dtm_name,
            extent="region",
            overwrite=True,
            quiet=True,
        )
        all_dtms.append(dtm_name)

    # Create VRT of tiles
    # (dont copy raster maps -> create real raster in the next steps)
    vrt = f"vrt_dtm_{output}_{ID}"
    rm_rasters.append(vrt)
    rm_rasters.extend(all_dtms)
    create_vrt(all_dtms, vrt, copy_raster_maps=False)

    # resample / interpolate whole VRT (because interpolating single files lead
    # to emplty rows and columns)
    # check resolution and resample / interpolate data if needed
    if not native_res:
        grass.message(_("Resampling / interpolating data..."))
        if alignment_raster:
            # set extent from imported data, and align with alignment raster
            grass.run_command("g.region", raster=vrt, align=alignment_raster)
            ns_res = float(
                grass.parse_command("r.info", map=alignment_raster, flags="g")[
                    "nsres"
                ],
            )
        else:
            # if no alignemnt raster is given,
            # use extent of imported data and
            # set and align with current region resolution
            grass.run_command("g.region", raster=vrt)
            grass.run_command("g.region", res=ns_res, flags="a")
        adjust_raster_resolution(vrt, output, ns_res)
    else:
        # Note: Want real raster/no VRT as output
        vrt_to_raster(vrt, output)

    grass.message(_(f"DTM raster map <{output}> is created."))

    if metadata_file and url_list:
        try:
            with pathlib.Path(metadata_file).open("w", encoding="utf-8") as f:
                f.writelines(f"{url}\n" for url in url_list)
            grass.debug("Wrote tile URLs to tempfile")
        except Exception as e:
            grass.warning(f"Could not write tempfile metadata: {e}")


if __name__ == "__main__":
    options, flags = grass.parser()
    atexit.register(cleanup)
    main()
