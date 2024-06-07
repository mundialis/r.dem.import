#!/usr/bin/env python3
#
############################################################################
#
# MODULE:      r.dtm.import.bb
# AUTHOR(S):   Anika Weinmann
#
# PURPOSE:     Downloads and imports DTM for Brandenburg and aoi
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
# % description: Downloads and imports DTM for Brandenburg and aoi.
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

from grass_gis_helpers.cleanup import cleaning_tmp_location, general_cleanup
from grass_gis_helpers.data_import import (
    download_and_import_tindex,
    get_list_of_tindex_locations,
    import_single_local_xyz_file,
)
from grass_gis_helpers.location import (
    create_tmp_location,
    get_current_location,
    switch_back_original_location,
)
from grass_gis_helpers.open_geodata_germany.download_data import (
    check_download_dir,
    download_data_using_threadpool,
    extract_compressed_files,
    fix_corrupted_data,
)
from grass_gis_helpers.raster import create_vrt

# set constant variables
TINDEX = (
    "https://github.com/mundialis/tile-indices/raw/main/DTM/BB/"
    "BB_tileindex_dgm_proj.gpkg.gz"
)
DATA_BASE_URL = "https://data.geobasis-bb.de/geobasis/daten/dgm/xyz/"
EPSGCODE = 25833
ID = grass.tempname(12)
ORIG_REGION = f"original_region_{ID}"

# set global variables
keep_data = False
download_dir = None
rm_files = []
rm_rasters = []
rm_vectors = []
gisdbase = None
tgtgisrc = None
tmploc = None
srcgisrc = None


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
        rm_files=rm_files,
    )
    # remove temp location and switch location
    cleaning_tmp_location(tgtgisrc, tmploc, gisdbase, srcgisrc)


def main():
    """Main function of r.dtm.import.bb"""
    global download_dir, rm_files, rm_rasters, rm_vectors, keep_data
    # global vars for temporary location
    global gisdbase, tgtgisrc, tmploc, srcgisrc

    aoi = options["aoi"]
    download_dir = check_download_dir(options["download_dir"])
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
    tindex_vect = f"dtm_tindex_{ID}"
    rm_vectors.append(tindex_vect)
    download_and_import_tindex(TINDEX, tindex_vect, download_dir)

    # get download urls which overlap with aoi
    url_tiles = get_list_of_tindex_locations(tindex_vect, aoi)

    # download XYZ DTM files
    # TODO check if nprocs 3 is ok or another values should be used
    grass.message(_("Downloading DTMs..."))
    urls = [
        f"{x.replace('/vsizip/vsicurl/', '').split('.zip/')[0]}.zip"
        for x in url_tiles
    ]
    download_data_using_threadpool(urls, download_dir, 3)

    # extract XYZ files
    grass.message(_("Extracting XYZ files from zip files..."))
    zip_filenames = [os.path.basename(url) for url in urls]
    extracted_files = extract_compressed_files(zip_filenames, download_dir)

    # import XYZ DTM files
    grass.message(_("Importing DTMs..."))
    grass.run_command("g.region", grow=1, quiet=True)
    data_files = [
        os.path.join(download_dir, file)
        for file in extracted_files
        if file.endswith(".xyz")
    ]
    all_dtms = []
    for data_file_name in data_files:
        dtm_name = os.path.splitext(os.path.basename(data_file_name))[
            0
        ].replace("-", "")
        data_file = os.path.join(download_dir, data_file_name)
        fix_corrupted_data(data_file)
        rm_files.append(f"{data_file}.bak")
        import_single_local_xyz_file(data_file, dtm_name, separator="comma")
        all_dtms.append(dtm_name)

    # create VRT
    create_vrt(all_dtms, output)

    # get native data resolution
    if native_res:
        res = float(
            grass.parse_command("r.info", map=output, flags="g")["nsres"]
        )

    # switch back to origin location
    switch_back_original_location(tgtgisrc)
    if not native_res:
        res = ns_res
    grass.run_command("g.region", vector=aoi, res=res, flags="a")
    grass.run_command(
        "r.proj",
        location=tmploc,
        mapset="PERMANENT",
        input=output,
        output=output,
        resolution=res,
        method="bilinear",
        flags="n",
        quiet=True,
        memory=1000,
    )
    grass.message(_(f"DTM raster map <{output}> is created."))


if __name__ == "__main__":
    options, flags = grass.parser()
    atexit.register(cleanup)
    main()
