#!/usr/bin/env python3
#
############################################################################
#
# MODULE:      r.dtm.import.mv
# AUTHOR(S):   Kim Kaiser, Anika Weinmann
# PURPOSE:     Downloads DTM for Mecklenburg-Vorpommern and aoi
# SPDX-FileCopyrightText: (c) 2026 by mundialis GmbH & Co. KG and the
#                             GRASS Development Team
# SPDX-License-Identifier: GPL-3.0-or-later.
#
############################################################################

# %module
# % description: Downloads DTM for Mecklenburg-Vorpommern and aoi.
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
from urllib.parse import urlparse, parse_qs
import grass.script as grass

from grass_gis_helpers.cleanup import (
    general_cleanup,
    cleaning_tmp_location,
)
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
from grass_gis_helpers.raster import (
    adjust_raster_resolution,
    create_vrt,
    vrt_to_raster,
)

# set variables
TINDEX = (
    "https://github.com/mundialis/tile-indices/raw/main/DTM/MV/"
    "mv_dtm_tindex_proj.gpkg.gz"
)
CURRENT_WORKING_DIR = os.getcwd()
EPSGCODE = 25833
ID = grass.tempname(12)
ORIG_REGION = f"original_region_{ID}"

keep_data = False
download_dir = None
rm_rasters = []
rm_vectors = []
gisdbase = None
tgtgisrc = None
tmploc = None
srcgisrc = None

def cleanup():
    """Cleaning up function"""
    os.chdir(CURRENT_WORKING_DIR)
    rm_dirs = []
    if not keep_data:
        if download_dir:
            rm_dirs.append(download_dir)
    general_cleanup(
        orig_region=ORIG_REGION,
        rm_rasters=rm_rasters,
        rm_vectors=rm_vectors,
        rm_dirs=rm_dirs,
        rm_mask=True,
    )
    # remove temp location and switch location
    cleaning_tmp_location(tgtgisrc, tmploc, gisdbase, srcgisrc)

def main():
    """Main function of r.dtm.import.mv"""
    global rm_rasters, rm_vectors, keep_data, download_dir
    # global vars for temporary location
    global gisdbase, tgtgisrc, tmploc, srcgisrc

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

    # get data files which overlap with aoi
    url_tiles = get_list_of_tindex_locations(tindex_vect, aoi)

    # import DTM GeoTiff files
    grass.message(_("Importing DTM..."))
    all_dtm = []
    for url in url_tiles:
        url_name = os.path.splitext(parse_qs(urlparse(url).query)["file"][0])[
            0
        ]
        dtm_name = url_name.strip("_gtiff")
        grass.run_command(
            "r.import",
            input=url,
            output=dtm_name,
            extent="region",
            overwrite=True,
            quiet=True,
        )
        all_dtm.append(dtm_name)

    # create VRT
    create_vrt(all_dtm, output)

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
