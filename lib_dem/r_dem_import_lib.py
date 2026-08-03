#!/usr/bin/env python3
#
############################################################################
#
# MODULE:      r_dem_import_lib
# AUTHOR(S):   Anika Weinmann, Kim Kaiser
# PURPOSE:     Library for r.dem.import
# SPDX-FileCopyrightText: (c) 2024-2026 by mundialis GmbH & Co. KG and the
#                             GRASS Development Team
# SPDX-License-Identifier: GPL-3.0-or-later.
#
############################################################################

import os
from time import sleep
import grass.script as grass

from grass_gis_helpers.data_import import (
    import_local_raster_data,
    import_local_xyz_files,
)

from grass_gis_helpers.general import set_nprocs

OPEN_DATA_AVAILABILITY = {
    "DTM": {
        "NO_OPEN_DATA": ["BW", "BY"],
        "NOT_YET_SUPPORTED": [
            # available data
            "RP",
            "ST",
            # no data available
            "MV",
            "SL",
        ],
        "SUPPORTED": [
            "BB",
            "BE",
            "HB",
            "HE",
            "HH",
            "NI",
            "NW",
            "SH",
            "SN",
            "TH",
        ],
    },
    "DSM": {
        "NO_OPEN_DATA": ["BW", "BY"],
        "NOT_YET_SUPPORTED": [
            # available data
            "NW",
            "ST",
            # no data available
            "MV",
            "RP",
            "SH",
            "SL",
        ],
        "SUPPORTED": [
            "BE",
            "HB",
            "HE",
            "NI",
            "SN",
            "TH",
        ],
    },
    "iDSM": {
        "NOT_YET_SUPPORTED": [
            # either not avaible, or not supported yet
            "BE",
            "BW",
            "BY",
            "HB",
            "HE",
            "MV",
            "NI",
            "RP",
            "SL",
            "ST",
            "SN",
            "TH",
        ],
        "SUPPORTED": [
            "BB",
            "HH",
            "NW",
            "SH",
        ],
    },
    "nDSM": {
        "NO_OPEN_DATA": ["BW", "BY"],
        "NOT_YET_SUPPORTED": [
            # calculated
            "BB",
            "BE",
            "HE",
            "HH",
            "SH",
            "TH",
            # available data
            "SN",
            "ST",
            # no data available
            "MV",
            "NI",
            "RP",
            "SL",
        ],
        "SUPPORTED": [
            "NW",
        ],
    },
}

WAITING_TIME = 10


def setup_parallel_processing(nprocs):
    """Get possible number of workers and modify environment variables
    Args:
        nprocs (int): Number of workers to use
    Returns:
        nprocs (int): Possible number of workers to use
    """
    nprocs = set_nprocs(nprocs)
    # set some common environmental variables, like:
    os.environ.update(
        {
            "GRASS_COMPRESSOR": "LZ4",
            "GRASS_MESSAGE_FORMAT": "plain",
        },
    )
    return nprocs


def create_grid_and_tiles_list(
    ns_res,
    ew_res,
    tile_size,
    grid,
    rm_vectors,
    aoi,
    id,
    fs,
):
    """Check if aoi is smaller than grid tile size and create grid if not.
    Also create a list containing tiles which overlap with the aoi.
    Args:
        ns_res (float): Vertical resolution
        ew_res (float): Horizontal resolution
        tile_size (int): Size of grid tiles to create
        grid (str): Name of grid to create
        rm_vectors (list): List of vectors to remove in cleanup
        aoi (str): Name of aoi
        id (str): id used in GRASS session
        fs (str): Abbreviation of federal state

    Returns:
        rm_vectors (list): Extended list of vectors to remove in cleanup
        number_tiles (str): Number of tiles overlapping with aoi
        tiles_list (list): List of tile names overlapping with aoi
    """
    # check if aoi is smaller than tile size
    if ns_res <= float(tile_size) and ew_res <= float(tile_size):
        grass.run_command("v.in.region", output=grid, quiet=True)
        rm_vectors.append(grid)
        grass.run_command(
            "v.db.addtable",
            map=grid,
            columns="cat int",
            quiet=True,
        )
    else:
        grass.run_command("g.region", res=tile_size, flags="a", quiet=True)

        # create grid
        grass.run_command(
            "v.mkgrid",
            map=grid,
            box=f"{tile_size},{tile_size}",
            quiet=True,
        )
        # reset region
        grass.run_command("g.region", vector=aoi)

    # set grid name
    grid_name = f"tmp_grid_area_{id}"

    # choose tiles overlapping with aoi
    grass.run_command(
        "v.select",
        ainput=grid,
        binput=aoi,
        output=grid_name,
        operator="overlap",
        quiet=True,
    )
    rm_vectors.append(grid_name)

    # create list of tiles
    tiles_num_list = list(
        grass.parse_command(
            "v.db.select",
            map=grid_name,
            columns="cat",
            flags="c",
            quiet=True,
        ).keys(),
    )
    number_tiles = len(tiles_num_list)

    grass.message(_(f"Number of tiles: {number_tiles}"))
    tiles_list = []
    for tile in tiles_num_list:
        tile_area = f"{fs}_DEM_{tile}_{id}"
        grass.run_command(
            "v.extract",
            input=grid_name,
            where=f"cat == {tile}",
            output=tile_area,
            quiet=True,
        )
        tiles_list.append(tile_area)
        rm_vectors.append(tile_area)

    return rm_vectors, number_tiles, tiles_list


def import_dem_from_wms(
    tile_key,
    raster_name,
    tile_url,
    resolution_to_import,
    layer_name,
    native_res,
    data_format="tiff",
    retries=10,
):
    """Import DEMs from WMS
    Args:
        tile_key (str): Key of current tile
        raster_name (str): Name of resulting raster
        tile_url (str): WMS URLs to get DEMs
        resolution_to_import (float): Resolution to resample imported raster to
        layer_name (str): Name of WMS Layer
        native_res (bool): Keep native DEM resolution
        retries (int): Set how often function is retried
    """

    # set region
    grass.run_command("g.region", vector=tile_key)
    if not native_res:
        grass.run_command("g.region", res=resolution_to_import, flags="a")
    tile_key = tile_key.split("@")[0]

    # import wms data and retry download if wms fails
    trydownload = True
    count = 0
    while trydownload:
        try:
            count += 1
            grass.run_command(
                "r.in.wms",
                url=tile_url,
                output=raster_name,
                layer=layer_name,
                format=data_format,
                overwrite=True,
            )
            trydownload = False
        except Exception:
            # remove maps where wms download failed
            grass.run_command(
                "g.remove",
                type="raster",
                pattern=raster_name,
                flags="f",
            )
            grass.message(_("Retry download..."))
            if count > retries:
                grass.fatal(f"Download of {tile_url} not working.")
            sleep(10)


def xyz_laz_clip_region_aoi(xyz_raster, output, aoi=None, region=None):
    """Clip imported xyz/laz-file to region/aoi

    r.in.pdal/r.in.xyz can not import only part of region/aoi.
    Thus clip in a follow up step
    Args:
        xyz_raster (str): Imported xyz/laz-file
        output (str): Clipped output raster map
        aoi (str): AOI if given
        region (str): Region (if no AOI given)

    """    
    if aoi:
        grass.run_command("g.region", vector=aoi, align=xyz_raster)
    elif region:
        grass.run_command("g.region", region=region, align=xyz_raster)
    else:
         grass.fatal("Neither 'region' nor 'aoi' is set, but one of them is required")
    grass.run_command(
        "r.mapcalc",
        expression=f"{output} = {xyz_raster}",
        quiet=True,
    )


def import_local_data(
        aoi,
        out,
        local_data_dir,
        fs,
        all_dems,
        rm_rasters,
        raster_type,
        native_res_flag=None,
    ):
    """Import local DEM raster data

    Args:
        aoi (str): Vector map with area of interest
        out (str): Base output name
        local_data_dir (str): Path to local data directory with federal state
                              subfolders
        fs (str): the abbrivation of the federal state
        all_dems (list): empty list where the imported DEM rasters
                         will be appended
        rm_rasters (list): List of rasters for cleanup, will be appended
        raster_type (string): Raster files type. Either raster or xyz
        native_res_flag (bool): True if native data resolution should be used
                                (only used for raster import)

    """
    if raster_type == "raster":
        imported_local_data = import_local_raster_data(
            aoi,
            f"{out}_{fs}",
            os.path.join(local_data_dir, fs),
            native_res_flag,
            all_dems,
            rm_rasters,
            band_dict=None,
        )
    elif raster_type == "xyz":
        if native_res_flag == None:
            grass.warning(_(
                "Note, that 'native_res_flag' will be ignored"
                "for local data import of xyz files."
            ))
        imported_local_data = import_local_xyz_files(
                aoi,
                f"{out}_{fs}",
                os.path.join(local_data_dir, fs),
                all_dems,
            )
    else:
        grass.fatal(_(
            f"Invalid raster_type for local data import: '{raster_type}'."
            "Valid ones are 'raster' or 'xyz'."))

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
