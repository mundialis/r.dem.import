#!/usr/bin/env python3
#
############################################################################
#
# MODULE:      r.dtm.import.sh
# AUTHOR(S):   Kim Kaiser
# PURPOSE:     Downloads DTM for Schleswig-Holstein
# SPDX-FileCopyrightText: (c) 2026 by mundialis GmbH & Co. KG and the
#                             GRASS Development Team
# SPDX-License-Identifier: GPL-3.0-or-later.
#
############################################################################

# %module
# % description: Downloads DTM for Schleswig-Holstein and aoi.
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
from urllib.parse import parse_qs, urlparse

import grass.script as grass
import requests
from grass.pygrass.utils import get_lib_path
from grass_gis_helpers.cleanup import general_cleanup
from grass_gis_helpers.data_import import (
    download_and_import_tindex,
    get_list_of_tindex_locations,
)
from grass_gis_helpers.open_geodata_germany.download_data import (
    check_download_dir,
)
from grass_gis_helpers.raster import adjust_raster_resolution, create_vrt

# import module library
path = get_lib_path(modname="r.dem.import")
if path is None:
    grass.fatal("Unable to find the dem library directory.")
sys.path.append(path)
try:
    from r_dem_import_lib import xyz_laz_clip_region_aoi
except Exception as imp_err:
    grass.fatal(f"r.dem.import library could not be imported: {imp_err}")

# set variables
TINDEX = (
    "https://github.com/mundialis/tile-indices/raw/main/DTM/SH/"
    "sh_dtm_tindex_proj.gpkg.gz"
)
CURRENT_WORKING_DIR = pathlib.Path.cwd()
ID = grass.tempname(12)
ORIG_REGION = f"original_region_{ID}"

keep_data = False
download_dir = None
rm_rasters = []
rm_vectors = []


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
    """Main function of r.dtm.import.sh."""
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
    tindex_vect = f"dtm_tindex_{ID}"
    rm_vectors.append(tindex_vect)
    download_and_import_tindex(TINDEX, tindex_vect, download_dir)

    # get download urls which overlap with aoi
    url_tiles = get_list_of_tindex_locations(tindex_vect, aoi)

    # download DTM files
    grass.message(_("Importing DTM..."))
    all_dtms = []
    for url in url_tiles:
        if aoi:
            grass.run_command("g.region", vector=aoi, flags="a")
        else:
            grass.run_command("g.region", region=ORIG_REGION)
        grass.run_command("g.region", res=1, grow=1, quiet=True)

        filename = parse_qs(urlparse(url).query)["file"][0]
        filepath = os.path.join(download_dir, filename)

        pathlib.Path(filepath).write_bytes(requests.get(url, timeout=10).content)

        # clean xyz file
        # SHs download endpoint appends HTML code after xyz file
        # workaround removes non-numeric lines before importing with r.in.xyz
        cleanfile = filepath + ".clean"
        with pathlib.Path(filepath).open("wb") as fin, pathlib.Path(cleanfile).open("w", encoding="utf-8") as fout:
            for line in fin:
                if line.startswith("<!DOCTYPE"):
                    break
                cols = line.split()
                if len(cols) != 3:
                    continue
                try:
                    float(cols[0])
                    float(cols[1])
                    float(cols[2])
                    fout.write(line)
                except ValueError:
                    continue
                fout.write(line)

        # import DTM files
        grass.run_command(
            "r.in.xyz",
            input=cleanfile,
            output=filename,
            separator="space",
            quiet=True,
            overwrite=True,
        )
        all_dtms.append(filename)
    rm_rasters.extend(all_dtms)

    # create VRT
    tmp_out = f"tmp_{output}_{ID}"
    rm_rasters.append(tmp_out)
    create_vrt(all_dtms, tmp_out, copy_raster_maps=False)

    # clip xyz-file to region /aoi
    if aoi:
        xyz_laz_clip_region_aoi(tmp_out, output, aoi=aoi)
    else:
        xyz_laz_clip_region_aoi(tmp_out, output, region=ORIG_REGION)

    # resample/interpolate whole VRT (because interpolating single files leads
    # to empty rows and columns)
    # check resolution and resample / interpolate data if needed
    if not native_res:
        if alignment_raster:
            # set extent from imported data, and align with alignment raster
            grass.run_command(
                "g.region", raster=output, align=alignment_raster,
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

    grass.message(_(f"DTM raster map <{output}> is created."))

    if metadata_file and url_tiles:
        try:
            with pathlib.Path(metadata_file).open("w", encoding="utf-8") as f:
                for url in url_tiles:
                    f.write(f"{url}\n")
            grass.debug("Wrote tile URLs to tempfile")
        except Exception as e:
            grass.warning(f"Could not write tempfile metadata: {e}")


if __name__ == "__main__":
    options, flags = grass.parser()
    atexit.register(cleanup)
    main()
