#!/usr/bin/env python3
#
############################################################################
#
# MODULE:      r.dem.wms.worker
# AUTHOR(S):   Johannes Halbauer, Kim Kaiser, Lina Krisztian, Leon Louwarts
# PURPOSE:     Imports Digital Elevation Models (DEMs) within a specified area via WMS
# SPDX-FileCopyrightText: (c) 2026 by mundialis GmbH & Co. KG and the
#                             GRASS Development Team
# SPDX-License-Identifier: GPL-3.0-or-later.
#
#############################################################################

# %Module
# % description: Imports single Digital Elevation Models (DEMs) via WMS
# % keyword: imagery
# % keyword: download
# % keyword: DEM
# %end

# %option G_OPT_V_INPUT
# % key: aoi
# % required: no
# % description: Vector map to restrict DEM import to
# %end

# %option
# % key: download_dir
# % label: Path to output folder
# % description: Path to download folder
# % required: no
# % multiple: no
# %end

# %option
# % key: tile_key
# % required: yes
# % description: Key of tile-DEM to import
# %end

# %option
# % key: tile_url
# % required: yes
# % description: WMS URL of tile-DEM to import
# %end

# %option
# % key: layer_names
# % required: yes
# % multiple: yes
# % description: Layer name of tile-DEM to import
# %end

# %option
# % key: new_mapset
# % type: string
# % required: yes
# % multiple: no
# % key_desc: name
# % description: Name for new mapset
# %end

# %option
# % key: orig_region
# % required: yes
# % description: Original region
# %end

# %option
# % key: resolution_to_import
# % required: no
# % description: Resolution of region, for which DEM will be imported (only if flag r not set)
# %end

# %option G_OPT_R_OUTPUT
# % key: raster_name
# % description: Name of raster output
# %end

# %flag
# % key: r
# % description: Use native DEM resolution
# %end


import atexit
import sys

import grass.script as grass
from grass.pygrass.utils import get_lib_path

from grass_gis_helpers.cleanup import general_cleanup
from grass_gis_helpers.location import switch_back_original_location
from grass_gis_helpers.mapset import switch_to_new_mapset

# import module library
path = get_lib_path(modname="r.dem.import")
if path is None:
    grass.fatal("Unable to find the dem library directory.")
sys.path.append(path)
try:
    from r_dem_import_lib import import_dem_from_wms
except Exception as imp_err:
    grass.fatal(f"r.dem.import library could not be imported: {imp_err}")

rm_rast = []
rm_group = []

# pylint: disable=C0103
original_nprocs = None

RETRIES = 30
WAITING_TIME = 10


def cleanup():
    """Remove all not needed files at the end"""
    general_cleanup(
        rm_rasters=rm_rast,
        rm_groups=rm_group,
    )
    """Reset nprocs"""
    if original_nprocs:
        grass.run_command("g.gisenv", set=f"NPROCS={original_nprocs}")
    else:
        grass.run_command("g.gisenv", unset="NPROCS")


def main():
    """Main function of r.dem.wms.worker"""
    global original_nprocs
    # parser options
    tile_key = options["tile_key"]
    tile_url = options["tile_url"]
    layer_names_string = options["layer_names"]
    raster_name = options["raster_name"]
    resolution_to_import = None
    if options["resolution_to_import"]:
        resolution_to_import = float(options["resolution_to_import"])
    orig_region = options["orig_region"]
    new_mapset = options["new_mapset"]

    layer_names_list = layer_names_string.split(",")

    # set nprocs to 1, write original value in variable
    gisenv = grass.gisenv()
    if "NPROCS" in gisenv:
        original_nprocs = int(gisenv["NPROCS"])
    grass.run_command("g.gisenv", set="NPROCS=1")

    # output resolution
    if not flags["r"] and not options["resolution_to_import"]:
        grass.fatal(
            "Use native resolution with the -r flag or specify "
            "'resolution_to_import'.",
        )

    # switch to new mapset for parallel processing
    gisrc, newgisrc, old_mapset = switch_to_new_mapset(new_mapset)

    # set region
    grass.run_command("g.region", region=f"{orig_region}@{old_mapset}")

    # import DEM tile with original resolution
    grass.message(
        _(
            f"Started DEM import for key: {tile_key} and URL: {tile_url}",
        ),
    )

    # add all generated rasters to a list, later used to create vrt
    raster_name_list = []

    # iterate through all layers
    for layer_name in layer_names_list:
        output_raster = f"{raster_name}_{layer_name}"

        # import DEMs from WMS
        import_dem_from_wms(
            f"{tile_key}@{old_mapset}",
            output_raster,
            tile_url,
            resolution_to_import,
            layer_name,
            flags["r"],
            "tiff",
        )
        raster_name_info = grass.raster_info(output_raster)

        # test if raster is invalid
        if (
            raster_name_info["min"] is not None
            and raster_name_info["max"] is not None
        ):
            raster_name_list.append(output_raster)
        else:
            rm_rast.append(output_raster)

    # no valid raster
    if not raster_name_list:
        grass.fatal("Unable to find DEM matching the given aoi")

    # one valid raster
    elif len(raster_name_list) == 1:
        grass.run_command(
            "g.rename",
            raster=f"{raster_name_list[0]},{raster_name}",
        )

    # multiple valid rasters
    else:
        grass.run_command(
            "r.patch",
            input=raster_name_list,
            output=raster_name,
        )

    grass.message(_(f"Finishing raster import for {raster_name}..."))

    # switch back to original location
    switch_back_original_location(gisrc)
    grass.utils.try_remove(newgisrc)
    grass.message(
        _(
            f"DEM import for key: {tile_key} and URL: {tile_url} done!",
        ),
    )


if __name__ == "__main__":
    options, flags = grass.parser()
    atexit.register(cleanup)
    main()
