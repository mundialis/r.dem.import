#!/usr/bin/env python3
#
############################################################################
#
# MODULE:      r.dtm.import
# AUTHOR(S):   Anika Weinmann, Leon Louwarts
# PURPOSE:     Downloads DTM for specified federal state and aoi
# SPDX-FileCopyrightText: (c) 2024 - 2026 by mundialis GmbH & Co. KG and the
#                             GRASS Development Team
# SPDX-License-Identifier: GPL-3.0-or-later.
#
############################################################################

# %module
# % description: Downloads and imports DTM for specified federal state and aoi.
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
# % key: federal_state
# % type: string
# % multiple: yes
# % required: no
# % options: Berlin,BE,Baden-Württemberg,Brandenburg,BB,BW,Bayern,BY,Bremen,HB,Hamburg,HH,Hessen,HE,Sachsen,NI,Niedersachsen,SN,Thüringen,TH,Nordrhein-Westfalen,NW
# % description: Federal state(s) related to the area of interest e.g.:"Nordrhein-Westfalen"
# %end

# %option G_OPT_F_INPUT
# % key: federal_state_file
# % description: Path to text file containing the federal state(s) related to the area of interest
# % required: no
# %end

# %option G_OPT_M_DIR
# % key: local_data_dir
# % required: no
# % description: Directory with raster map of DTMs to import (e.g. XYZ/TXT files)
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
# % key: metadata
# % type: string
# % required: no
# % multiple: no
# % description: Path to metadata output file (markdown format)
# % answer:
# %end

# %option
# % key: metadata_file
# % type: string
# % required: no
# % description: Temporary file for metadata URLs (used by r.ndsm.import)
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
from grass.pygrass.utils import get_lib_path

from grass_gis_helpers.cleanup import general_cleanup
from grass_gis_helpers.data_import import import_local_xyz_files
from grass_gis_helpers.open_geodata_germany.download_data import (
    check_download_dir,
)
from grass_gis_helpers.open_geodata_germany.federal_state import (
    get_federal_states,
)
from grass_gis_helpers.open_geodata_germany.metadata import (
    collect_metadata,
    get_license_and_url_from_addon,
    write_metadata_markdown,
)
from grass_gis_helpers.raster import create_vrt

# import module library
path = get_lib_path(modname="r.dem.import")
if path is None:
    grass.fatal("Unable to find the dem library directory.")
sys.path.append(path)
try:
    from r_dem_import_lib import OPEN_DATA_AVAILABILITY
    from r_dem_import_metadata_lib import get_download_urls_and_names
except Exception as imp_err:
    grass.fatal(f"r.dem.import library could not be imported: {imp_err}")

# set constant variables
ID = grass.tempname(12)
ORIG_REGION = f"original_region_{ID}"
NO_OPEN_DATA = OPEN_DATA_AVAILABILITY["DTM"]["NO_OPEN_DATA"]
NOT_YET_SUPPORTED = OPEN_DATA_AVAILABILITY["DTM"]["NOT_YET_SUPPORTED"]
# set global variables
rm_rasters = []


def cleanup():
    """Cleaning up function"""
    general_cleanup(
        orig_region=ORIG_REGION,
        rm_rasters=rm_rasters,
    )


def import_local_data(aoi, out, local_data_dir, fs, all_dtms):
    """Import local DTM data

    Args:
        aoi (str): Vector map with area of interest
        out (str): Base output name
        local_data_dir (str): Path to local data directory with federal state
                              subfolders
        fs (str): the abbrivation of the federal state
        all_dtms (list): empty list where the imported DTM rasters
                         will be appended
    """
    imported_local_data = import_local_xyz_files(
        aoi,
        f"{out}_{fs}",
        os.path.join(local_data_dir, fs),
        all_dtms,
    )

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


def get_addon_name(fs):
    """Function to get the addon name for the function to get license info"""
    return f"r.dtm.import.{fs.lower()}"


def main():
    """Main function of r.dtm.import"""
    global rm_rasters

    aoi = options["aoi"]
    federal_states = get_federal_states(
        options["federal_state"], options["federal_state_file"]
    )
    local_data_dir = options["local_data_dir"]
    download_dir = check_download_dir(options["download_dir"])
    alignment_raster = options["alignment_raster"]
    metadata_path = options["metadata"]
    output = options["output"]
    keep_data = flags["k"]
    native_res = flags["r"]

    # save original region
    grass.run_command("g.region", save=ORIG_REGION, quiet=True)

    # local DTM files
    local_fs_list = []
    if local_data_dir and local_data_dir != "":
        local_fs_list = os.listdir(local_data_dir)

    # loop over federal states and import data
    all_dtms = []
    metadata_list = []
    for fs in set(federal_states):
        fs_dem_list = []
        dem_names = []
        dem_urls = []

        # check if local data for federal state given
        imported_local_data = False
        if fs in local_fs_list:
            imported_local_data = import_local_data(
                aoi, output, local_data_dir, fs, all_dtms
            )
            if imported_local_data:
                fs_dem_list = [f"{output}_{fs}"]
                local_fs_dir = os.path.join(local_data_dir, fs)
                if pathlib.Path(local_fs_dir).exists():
                    for _root, _dirs, files in os.walk(local_fs_dir):
                        dem_names.extend(
                            file
                            for file in files
                            if file.lower().endswith(
                                (".tif", ".tiff", ".jp2", ".jpeg"),
                            )
                        )
        elif fs in NO_OPEN_DATA:
            grass.fatal(
                _(
                    f"No local data for {fs} available. For the federal state "
                    "there are no open data available. Is the path correct?"
                )
            )

        # import data when local import was not used
        if not imported_local_data:
            if fs in NOT_YET_SUPPORTED:
                grass.fatal(
                    _(
                        "The import of the open data is not yet supported for "
                        f"{fs}."
                    )
                )
            elif fs in NO_OPEN_DATA:
                grass.fatal(
                    _(
                        f"For the federal state {fs} there are no open data "
                        "available. Please use local data <local_data_dir>."
                    )
                )
            # implement data download and import from open data
            r_dtm_import_fs_flags = ""
            if keep_data:
                r_dtm_import_fs_flags += "k"
            if native_res:
                r_dtm_import_fs_flags += "r"
            out_fs = f"dtm_{fs}_{ID}"
            addon = f"r.dtm.import.{fs.lower()}"
            params = {
                "aoi": aoi,
                "download_dir": download_dir,
                "alignment_raster": alignment_raster,
                "output": out_fs,
                "flags": r_dtm_import_fs_flags,
                "overwrite": True,
            }
            # Only create a tempfile for URL/metadata exchange with the
            # state-specific addon if a metadata file was actually
            # requested by the user
            metadata_tmpfile = options.get("metadata_file") or None
            if not metadata_tmpfile and metadata_path:
                metadata_tmpfile = grass.tempfile()
            if metadata_tmpfile:
                params["metadata_file"] = metadata_tmpfile

            grass.run_command(addon, **params)
            all_dtms.append(out_fs)
            fs_dem_list = [out_fs]

            if metadata_tmpfile:
                # Reads URLs from the tempfile written by the addon, with
                # fallbacks to the download directory and raster count
                # if no URLs could be determined (see
                # r_dem_import_metadata_lib.py)
                dem_urls, dem_names = get_download_urls_and_names(
                    metadata_tmpfile=metadata_tmpfile,
                    keep_data=keep_data,
                    download_dir=download_dir,
                    out_fs=out_fs,
                    fs=fs,
                )

                # Collect metadata for this federal state (license/source info comes from
                # the addon's HTML documentation, file/URL info from above)
                addon_name = get_addon_name(fs)
                license_info, base_url = get_license_and_url_from_addon(addon_name)
                fs_metadata = collect_metadata(
                    fs=fs,
                    raster_list=fs_dem_list,
                    license_info=license_info,
                    base_url=base_url,
                    original_names=dem_names,
                    download_urls=dem_urls,
                )
                metadata_list.append(fs_metadata)

    create_vrt(all_dtms, output)
    grass.message(_(f"DTM raster map <{output}> is created."))

    # Write metadata file if metadata_path was set
    write_metadata_markdown(
        metadata_list=metadata_list,
        metadata_path=metadata_path,
        data_label="DGM",
    )


if __name__ == "__main__":
    options, flags = grass.parser()
    atexit.register(cleanup)
    main()
