#!/usr/bin/env python3
#
############################################################################
#
# MODULE:      r.dsm.import.th
# AUTHOR(S):   Anika Weinmann
#
# PURPOSE:     Downloads DSM for Thüringen and aoi
# COPYRIGHT:   (C) 2024 by mundialis GmbH & Co. KG and the GRASS
#              Development Team
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
############################################################################

# %module
# % description: Downloads DSM for Thüringen and aoi.
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
# %end

import atexit
import os

import grass.script as grass

from grass_gis_helpers.cleanup import general_cleanup
from grass_gis_helpers.data_import import (
    download_and_import_tindex,
    get_list_of_tindex_locations,
    import_single_local_xyz_file,
)
from grass_gis_helpers.open_geodata_germany.download_data import (
    check_download_dir,
    download_data_using_threadpool,
    extract_compressed_files,
)
from grass_gis_helpers.raster import adjust_raster_resolution, create_vrt

# set constant variables
TINDEX = (
    "https://github.com/mundialis/tile-indices/raw/main/DSM/TH/"
    "TH_DOM_tileindex_proj.gpkg.gz"
)
DATA_BASE_URL = (
    "https://geoportal.geoportal-th.de/hoehendaten/DOM/dom_2014-2019/"
)
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
    """Main function of r.dsm.import.th"""
    global rm_rasters, rm_vectors, keep_data, download_dir

    aoi = options["aoi"]
    download_dir = check_download_dir(options["download_dir"])
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

    # download XYZ DSM files
    # TODO check if nprocs 3 is ok or another values should be used
    grass.message(_("Downloading DSMs..."))
    urls = [
        f"{x.replace('/vsizip/vsicurl/', '').split('.zip/')[0]}.zip"
        for x in url_tiles
    ]
    download_data_using_threadpool(urls, download_dir, 3)

    # extract XYZ files
    grass.message(_("Extracting XYZ files from zip files..."))
    zip_filenames = [os.path.basename(url) for url in urls]
    extract_compressed_files(zip_filenames, download_dir)

    # import XYZ DSM files
    grass.message(_("Importing DSMs..."))
    grass.run_command("g.region", grow=1, quiet=True)
    xyz_files = [os.path.basename(url_tile) for url_tile in url_tiles]
    all_dsms = []
    for xyz_file_name in xyz_files:
        dsm_name = os.path.splitext(os.path.basename(xyz_file_name))[
            0
        ].replace("-", "")
        xyz_file = os.path.join(download_dir, xyz_file_name)
        import_single_local_xyz_file(xyz_file, dsm_name)
        all_dsms.append(dsm_name)

    # create VRT
    create_vrt(all_dsms, output)

    # resample / interpolate whole VRT (because interpolating single files lead
    # to emplty rows and columns)
    # check resolution and resample / interpolate data if needed
    if not native_res:
        grass.run_command("g.region", raster=output, res=ns_res)
        grass.message(_("Resampling / interpolating data..."))
        adjust_raster_resolution(output, output, ns_res)

    grass.message(_(f"DSM raster map <{output}> is created."))


if __name__ == "__main__":
    options, flags = grass.parser()
    atexit.register(cleanup)
    main()
