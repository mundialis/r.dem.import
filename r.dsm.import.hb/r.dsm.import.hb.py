#!/usr/bin/env python3
#
############################################################################
#
# MODULE:      r.dsm.import.hb
# AUTHOR(S):   Kim Kaiser, Veronica Koess, Anika Weinmann
# PURPOSE:     Downloads DSM for Bremen/Bremerhaven
# SPDX-FileCopyrightText: (c) 2026 by mundialis GmbH & Co. KG and the
#                             GRASS Development Team
# SPDX-License-Identifier: GPL-3.0-or-later.
#
############################################################################

# %module
# % description: Downloads DSM for Bremen/Bremerhaven
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
# % key: nprocs
# % type: integer
# % required: no
# % multiple: no
# % label: Number of parallel processes
# % description: Number of cores for multiprocessing, -2 is the number of available cores - 1
# % answer: -2
# %end

# %option G_OPT_MEMORYMB
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
import sys

import grass.script as grass
from grass.pygrass.modules import Module, ParallelModuleQueue
from grass.pygrass.utils import get_lib_path

from grass_gis_helpers.cleanup import general_cleanup
from grass_gis_helpers.raster import adjust_raster_resolution, create_vrt

# import module library
path = get_lib_path(modname="r.dem.import")
if path is None:
    grass.fatal("Unable to find the dem library directory.")
sys.path.append(path)
try:
    from r_dem_import_lib import (
        setup_parallel_processing,
        create_grid_and_tiles_list,
    )
except Exception as imp_err:
    grass.fatal(f"r.dem.import library could not be imported: {imp_err}")

ID = grass.tempname(12)
ORIG_REGION = f"original_region_{ID}"
rm_vectors = []
rm_rasters = []
download_dir = None
rm_dirs = []

WMS_URL = (
    "https://geodienste.bremen.de/wms_dom1?REQUEST=GetCapabilities&SERVICE"
    "=WMS&VERSION=1.3.0&"
)
LAYER = ["DOM1_HB", "DOM1_BHV"]
NATIVE_DSM_RES = 1


def cleanup():
    """Remove all not needed files at the end"""
    general_cleanup(
        orig_region=ORIG_REGION,
        rm_vectors=rm_vectors,
        rm_rasters=rm_rasters,
        rm_dirs=rm_dirs,
    )


def main():
    """Main function of r.dsm.import.hb"""
    global rm_vectors
    aoi = options["aoi"]
    alignment_raster = options["alignment_raster"]
    nprocs = int(options["nprocs"])
    nprocs = setup_parallel_processing(nprocs)
    output = options["output"]
    fs = "HB"

    # print warning that memory will be ignored
    # (no memory parameter in worker module)
    if options["memory"]:
        grass.warning(
            _(
                "<memory> parameter will be ignored, because the worker "
                "module for DEMs does not accept a <memory> parameter.",
            ),
        )

    # if -k flag is set print warning that it will be ignored because
    # the data will be directly imported into GRASS from WMS
    if flags["k"]:
        grass.warning(
            _(
                "-k flag will be ignored, beacuse HB DEMs will be imported "
                "directly from WMS into GRASS. Use r.out.gdal module to "
                "export DSMs into download directory!",
            ),
        )

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

    # create grid for downloading
    grass.message(_("Creating DSM tiles for HB..."))

    # set tile size in map units (meter)
    tile_size = 1000

    # set grid name
    grid = f"tmp_grid_HB_{ID}"

    # create grid with lib function
    rm_vectors, number_tiles, tiles_list = create_grid_and_tiles_list(
        ns_res,
        ns_res,
        tile_size,
        grid,
        rm_vectors,
        aoi,
        ID,
        fs,
    )

    # set number of parallel processes to number of tiles
    if number_tiles < nprocs:
        nprocs = number_tiles
    queue = ParallelModuleQueue(nprocs=nprocs)

    # get GISDBASE and Location
    gisenv = grass.gisenv()
    gisdbase = gisenv["GISDBASE"]
    location = gisenv["LOCATION_NAME"]

    # set queue and variables for worker addon
    create_vrt_list = []
    try:
        grass.message(
            _(f"Importing {number_tiles} DSMs for HB in parallel..."),
        )
        for tile in tiles_list:
            key = tile
            new_mapset = f"tmp_mapset_r_dem_import_tile_{key}_{os.getpid()}"
            rm_dirs.append(os.path.join(gisdbase, location, new_mapset))
            raster_name = tile
            create_vrt_list.append(f"{raster_name}@{new_mapset}")
            param = {
                "tile_key": key,
                "tile_url": WMS_URL,
                "layer_names": ",".join(LAYER),
                "raster_name": raster_name,
                "orig_region": ORIG_REGION,
                "new_mapset": new_mapset,
                "flags": "",
            }
            grass.message(_(f"raster name: {raster_name}"))

            # modify params
            if aoi:
                param["aoi"] = aoi
            if flags["r"]:
                param["resolution_to_import"] = NATIVE_DSM_RES
            else:
                param["resolution_to_import"] = ns_res

            # run worker addon in parallel
            r_dem_wms_worker = Module(
                "r.dem.wms.worker",
                **param,
                run_=False,
            )
            # catch all GRASS output to stdout and stderr
            r_dem_wms_worker.stdout = grass.PIPE
            r_dem_wms_worker.stderr = grass.PIPE
            queue.put(r_dem_wms_worker)
        queue.wait()
    except Exception:
        for proc_num in range(queue.get_num_run_procs()):
            proc = queue.get(proc_num)
            if proc.returncode != 0:
                # save all stderr to a variable and pass it to a GRASS
                # exception
                errmsg = proc.outputs["stderr"].value.strip()
                grass.fatal(
                    _(f"\nERROR by processing <{proc.get_bash()}>: {errmsg}"),
                )

    create_vrt(create_vrt_list, output)
    if not flags["r"]:
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

    grass.message(_(f"Generated following raster map: {output}"))


if __name__ == "__main__":
    options, flags = grass.parser()
    atexit.register(cleanup)
    main()
