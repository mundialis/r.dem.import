#!/usr/bin/env python3
#
############################################################################
#
# MODULE:      r.idsm.import.rp
# AUTHOR(S):   Kim Kaiser, Lina Krisztian
# PURPOSE:     Downloads iDSM for Rheinland-Pfalz and aoi
# SPDX-FileCopyrightText: (c) 2026 by mundialis GmbH & Co. KG and the
#                             GRASS Development Team
# SPDX-License-Identifier: GPL-3.0-or-later.
#
############################################################################

# %module
# % description: Downloads iDSM for Rheinland-Pfalz and aoi.
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
import pathlib
from urllib.parse import parse_qs, urlparse

import grass.script as grass
from grass_gis_helpers.cleanup import general_cleanup
from grass_gis_helpers.data_import import (
    download_and_import_tindex,
    get_list_of_tindex_locations,
    import_single_local_las_file,
)
from grass_gis_helpers.open_geodata_germany.download_data import (
    check_download_dir,
    download_data_using_threadpool,
)
from grass_gis_helpers.raster import create_vrt

# set constant variables
TINDEX = (
    "https://github.com/kimariak/tile-indices/raw/rp_tindex/iDSM/RP/"
    "rp_idsm_tindex_proj.gpkg.gz"

    # "https://github.com/mundialis/tile-indices/raw/main/iDSM/RP/"
    # "rp_idsm_tindex_proj.gpkg.gz"
)
RESOLUTION = 0.2
ID = grass.tempname(12)
ORIG_REGION = f"original_region_{ID}"

# set global variables
keep_data = False
download_dir = None
rm_rasters = []
rm_vectors = []


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
    """Main function of r.idsm.import.rp."""
    global keep_data, download_dir

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
        idsm_name = pathlib.Path(url).name[0]
        las_file = os.path.join(download_dir, f"{idsm_name}.laz")
        import_single_local_las_file(las_file, idsm_name, RESOLUTION)

        # # TODO: Interpolieren dauert lange/braucht viel Speicher.
        # # Deshalb Abfrage, ob NoData cells vorhanden sind, einbauen.
        # # Vlt noch Options anpassen/ Ideen zu Speicher?

        # # interpolate NoData cells using IDW
        # # region res should be set to RESOLUTION since interpolation
        # # will be in current region resolution
        # grass.message(_("Interpolating data..."))
        # grass.run_command("g.region", res=RESOLUTION, flags="a")
        # grass.run_command(
        #     "r.fill.stats",
        #     input=tmp_out,
        #     output=idsm_name,
        #     distance=3,
        #     mode="wmean",
        #     power=2.0,
        #     cells=8,
        #     flags="k",
        #     quiet=True,
        # )
        all_idsms.append(idsm_name)

    # Create VRT of tiles
    # (dont copy raster maps -> create real raster in the next steps)
    vrt = f"vrt_idsm_{output}_{ID}"
    rm_rasters.append(vrt)
    rm_rasters.extend(all_idsms)
    create_vrt(all_idsms, vrt, copy_raster_maps=False)

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

    grass.message(_(f"iDSM raster map <{output}> is created."))

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
