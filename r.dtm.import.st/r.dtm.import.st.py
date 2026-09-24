#!/usr/bin/env python3
#
############################################################################
#
# MODULE:      r.dtm.import.st
# AUTHOR(S):   Kim Kaiser, Veronica Koess, Anika Weinmann
# PURPOSE:     Downloads DTM for Sachsen-Anhalt
# SPDX-FileCopyrightText: (c) 2026 by mundialis GmbH & Co. KG and the
#                             GRASS Development Team
# SPDX-License-Identifier: GPL-3.0-or-later.
#
############################################################################

# %module
# % description: Downloads DTM for Sachsen-Anhalt
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
# % key: nprocs
# % type: integer
# % required: no
# % multiple: no
# % label: Number of parallel processes
# % description: Number of cores for multiprocessing, -2 is the number of available cores - 1
# % answer: -2
# %end

# %option
# % key: metadata_file
# % type: string
# % required: no
# % description: Temporary file for metadata URLs
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
import pathlib

import grass.script as grass
from grass.pygrass.modules import Module, ParallelModuleQueue
from grass.pygrass.utils import get_lib_path
from grass_gis_helpers.cleanup import general_cleanup
from grass_gis_helpers.data_import import (
    download_and_import_tindex,
    get_list_of_tindex_locations,
)
from grass_gis_helpers.open_geodata_germany.download_data import (
    check_download_dir,
)
from grass_gis_helpers.raster import (
    adjust_raster_resolution,
    create_vrt,
    vrt_to_raster,
)

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

# set variables
WCS_URL = ("https://www.geodatenportal.sachsen-anhalt.de/ows_WCS_ST_DGM1")
LAYER = ("Coverage1")
NATIVE_DTM_RES = 1

CURRENT_WORKING_DIR = pathlib.Path.cwd()
ID = grass.tempname(12)
ORIG_REGION = f"original_region_{ID}"

keep_data = False
download_dir = None
rm_vectors = []
rm_rasters = []
rm_dirs = []

def cleanup():
    """Cleaning up function."""
    os.chdir(CURRENT_WORKING_DIR)
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
    """Main function of r.dtm.import.st"""
    global keep_data, download_dir, rm_rasters, rm_vectors, rm_dirs

    aoi = options["aoi"]
    download_dir = check_download_dir(options["download_dir"]) 
    alignment_raster = options["alignment_raster"]
    metadata_file = options["metadata_file"]
    nprocs = int(options["nprocs"])
    nprocs = setup_parallel_processing(nprocs)
    output = options["output"]
    fs = "ST"
    keep_data = flags["k"]
    native_res = flags["r"]

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
    # the data will be directly imported into GRASS from WCS
    if flags["k"]:
        grass.warning(
            _(
                "-k flag will be ignored, beacuse ST DEMs will be imported "
                "directly from WCS into GRASS. Use r.out.gdal module to "
                "export DTMs into download directory!",
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
    grass.message(_("Creating DTM tiles for ST..."))

    # set tile size in map units (meter)
    tile_size = 1000

    # set grid name
    grid = f"tmp_grid_ST_{ID}"

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
            _(f"Importing {number_tiles} DTMs for ST in parallel..."),
        )
        for tile in tiles_list:
            key = tile
            new_mapset = f"tmp_mapset_r_dem_import_tile_{key}_{os.getpid()}"
            rm_dirs.append(os.path.join(gisdbase, location, new_mapset))
            raster_name = tile
            create_vrt_list.append(f"{raster_name}@{new_mapset}")
            param = {
                "tile_key": key,
                "tile_url": WCS_URL,
                "layer_names": LAYER,
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
                param["resolution_to_import"] = NATIVE_DTM_RES
            else:
                param["resolution_to_import"] = ns_res
            import pdb; pdb.set_trace()
            # run worker addon in parallel
            r_dem_wcs_worker = Module(
                "r.dem.wcs.worker",
                **param,
                run_=False,
            )
            # catch all GRASS output to stdout and stderr
            r_dem_wcs_worker.stdout = grass.PIPE
            r_dem_wcs_worker.stderr = grass.PIPE
            queue.put(r_dem_wcs_worker)
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

    # Create VRT of tiles
    # (dont copy raster maps -> create real raster in the next steps)
    vrt = f"vrt_dtm_{output}_{ID}"
    rm_rasters.append(vrt)
    rm_rasters.extend(create_vrt_list)
    create_vrt(create_vrt_list, vrt, copy_raster_maps=False)

    # resample / interpolate whole VRT (because interpolating single files leads
    # to empty rows and columns)
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
        rm_rasters.append(f"{output}_tmp")

    grass.message(_(f"DTM raster map <{output}> is created."))

    if metadata_file and url_tiles:
        try:
            with pathlib.Path(metadata_file).open("w", encoding="utf-8") as f:
                for url in url_tiles:
                    f.write(f"{url}\n")
            grass.debug("Wrote tile URLs to tempfile")
        except Exception as e:
            grass.warning(f"Could not write tempfile metadata: {e}")



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
