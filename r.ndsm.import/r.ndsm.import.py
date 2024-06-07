#!/usr/bin/env python3
#
############################################################################
#
# MODULE:      r.ndsm.import
# AUTHOR(S):   Anika Weinmann
#
# PURPOSE:     Downloads digital surface models (DSM) and digital terrain models (DTM)
#              for specified federal state and area of interest,
#              and creates a single file of a normalised DSM (nDSM) in GRASS.
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
# % description: Downloads DSM and DTM for specified federal state and aoi and creates a single file of a normalised DSM.
# % keyword: raster
# % keyword: import
# % keyword: nDSM
# % keyword: nDOM
# % keyword: DOM
# % keyword: DSM
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
# % required: no
# % multiple: yes
# % description: Federal state(s) related to the area of interest e.g.:"Nordrhein-Westfalen"
# %end

# %option G_OPT_F_INPUT
# % key: federal_state_file
# % description: Path to text file containing the federal state(s) related to the area of interest
# % required: no
# %end

# %option G_OPT_M_DIR
# % key: local_data_dir_ndsm
# % required: no
# % description: Directory with raster map of nDSMs to import (e.g. VRT)
# %end

# %option G_OPT_M_DIR
# % key: local_data_dir_dsm
# % required: no
# % description: Directory with raster map of DSMs to import (e.g. VRT)
# %end

# %option G_OPT_M_DIR
# % key: local_data_dir_dtm
# % required: no
# % description: Directory with raster map of DTMs to import (e.g. VRT)
# %end

# %option
# % key: download_dir
# % label: Path to output folder
# % description: path of download folder
# % required: no
# % multiple: no
# %end

# %option G_OPT_R_OUTPUT
# % description: Name for output raster map
# %end

# %flag
# % key: k
# % label: keep downloaded data in the downloaddirectory
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
import sys

import grass.script as grass
from grass.pygrass.utils import get_lib_path

from grass_gis_helpers.cleanup import general_cleanup
from grass_gis_helpers.open_geodata_germany.download_data import (
    check_download_dir,
)
from grass_gis_helpers.open_geodata_germany.federal_state import (
    get_federal_states,
)
from grass_gis_helpers.raster import create_vrt

# import module library
path = get_lib_path(modname="r.dem.import")
if path is None:
    grass.fatal("Unable to find the dem library directory.")
sys.path.append(path)
try:
    from r_dem_import_lib import OPEN_DATA_AVAILABILITY
except Exception as imp_err:
    grass.fatal(f"r.dem.import library could not be imported: {imp_err}")

# set constant variables
ID = grass.tempname(12)
ORIG_REGION = f"original_region_{ID}"

# set global variables
rm_rasters = []


def cleanup():
    """Cleaning up function"""
    general_cleanup(
        orig_region=ORIG_REGION,
        rm_rasters=rm_rasters,
        rm_mask=True,
    )


def compute_ndsm(dtm, dsm, ndsm):
    """Compute nDSM out of DTM and DSM

    Args:
        dtm (str): Name of DTM input raster map
        dsm (str): Name of DSM input raster map
        ndsm (str): Name for output nDSM raster map
    """
    grass.run_command("g.region", raster=dsm)
    grass.run_command(
        "r.mapcalc",
        expression=f"{ndsm} = {dsm} - {dtm}",
        quiet=True,
    )


def check_completeness_of_ndsm(aoi, ndsm):
    """Check if nDSM overlap complete area of interest

    Args:
        aoi (str): Name of aoi vector map
        ndsm (str): Name of nDSM input raster map
    """
    grass.run_command("g.region", raster=ndsm)
    if aoi:
        grass.run_command("r.mask", vector=aoi, quiet=True)
    check_output = f"output_null_cells_{ID}"
    rm_rasters.append(check_output)
    grass.run_command(
        "r.mapcalc",
        expression=f"{check_output}=if(isnull({ndsm}),null(),1)",
        quiet=True,
    )
    check_output_univar = grass.parse_command(
        "r.univar", map=check_output, flags="g"
    )
    if "nan" in check_output_univar["mean"]:
        grass.fatal(
            _(
                "Null cells contained within ndsm. Check if ndsm is imported "
                "for complete aoi/region."
            )
        )


def main():
    """Main function of r.ndsm.import"""
    global rm_rasters

    aoi = options["aoi"]
    federal_states = get_federal_states(
        options["federal_state"], options["federal_state_file"]
    )
    local_data_dir_ndsm = options["local_data_dir_ndsm"]
    local_data_dir_dsm = options["local_data_dir_dsm"]
    local_data_dir_dtm = options["local_data_dir_dtm"]
    download_dir = check_download_dir(options["download_dir"])
    output = options["output"]
    keep_data = flags["k"]
    nativ_res = flags["r"]

    # save orig region
    grass.run_command("g.region", save=ORIG_REGION, quiet=True)

    # local nDSM files
    local_ndsm_fs_list = []
    if local_data_dir_ndsm and local_data_dir_ndsm != "":
        local_ndsm_fs_list = os.listdir(local_data_dir_ndsm)
        grass.fatal(_("Local nDSM data dir is not yet supported."))

    # local DSM files
    local_dsm_fs_list = []
    if local_data_dir_dsm and local_data_dir_dsm != "":
        local_dsm_fs_list = os.listdir(local_data_dir_dsm)

    # local DTM files
    local_dtm_fs_list = []
    if local_data_dir_dtm and local_data_dir_dtm != "":
        local_dtm_fs_list = os.listdir(local_data_dir_dtm)

    ndsm_list = []
    for fs in federal_states:
        grass.run_command("g.region", region=ORIG_REGION)
        ndsm_out = None
        dtm_out = None
        dsm_out = None
        # check if local data for federal state given
        imported_local_data = False
        # TODO import local nDSM
        if fs in local_ndsm_fs_list:
            grass.message(_("Local nDSM import not yet supported!"))
        #     imported_local_data = import_local_data(
        #         aoi_map, local_data_dir, fs, output_alkis_fs
        #     )
        # elif fs in OPEN_DATA_AVAILABILITY["nDSM"]["NO_OPEN_DATA"]:
        #     grass.fatal(
        #         _(f"No local data for {fs} available. Is the path correct?")
        #     )

        # set flags for nDSM, DSM and DTM
        import_flags = ""
        if nativ_res:
            import_flags += "r"
        if keep_data:
            import_flags += "k"

        # import not local nDSM data
        if (
            imported_local_data is False
            and fs in OPEN_DATA_AVAILABILITY["nDSM"]["SUPPORTED"]
        ):
            grass.message(_(f"Importing nDSM data for {fs}..."))
            ndsm_out = f"ndsm_{fs}_{ID}"
            rm_rasters.append(ndsm_out)
            grass.run_command(
                f"r.ndsm.import.{fs.lower()}",
                aoi=aoi,
                download_dir=os.path.join(download_dir, "nDSM"),
                output=ndsm_out,
                flags=import_flags,
                quiet=True,
                overwrite=True,
            )

        # import DSM data
        if (
            imported_local_data is False
            and (
                fs in local_dsm_fs_list
                or fs in OPEN_DATA_AVAILABILITY["DSM"]["SUPPORTED"]
            )
        ) and ndsm_out is None:
            grass.message(_(f"Importing DSM data for {fs}..."))
            dsm_out = f"dsm_{fs}_{ID}"
            rm_rasters.append(dsm_out)
            grass.run_command(
                "r.dsm.import",
                aoi=aoi,
                federal_state=fs,
                local_data_dir=local_data_dir_dsm,
                download_dir=os.path.join(download_dir, "DSM"),
                output=dsm_out,
                flags=import_flags,
                quiet=True,
            )
            raster_info = grass.raster_info(dsm_out)["comments"].split()
            if raster_info[0].replace('"', "") in ["r.buildvrt", "r.patch"]:
                dsm_rasters = [
                    x.replace("input=", "")
                    .replace("\\", "")
                    .replace('"', "")
                    .split(",")
                    for x in raster_info
                    if x.startswith("input=")
                ][0]
                rm_rasters.extend(dsm_rasters)

        # import DTM data
        if (
            imported_local_data is False
            and (
                fs in local_dtm_fs_list
                or fs in OPEN_DATA_AVAILABILITY["DTM"]["SUPPORTED"]
            )
        ) and ndsm_out is None:
            grass.message(_(f"Importing DTM data for {fs}..."))
            dtm_out = f"dtm_{fs}_{ID}"
            rm_rasters.append(dtm_out)
            grass.run_command(
                "r.dtm.import",
                aoi=aoi,
                federal_state=fs,
                local_data_dir=local_data_dir_dtm,
                download_dir=os.path.join(download_dir, "DTM"),
                output=dtm_out,
                flags=import_flags,
                quiet=True,
            )
            raster_info = grass.raster_info(dtm_out)["comments"].split()
            if raster_info[0].replace('"', "") in ["r.buildvrt", "r.patch"]:
                dtm_rasters = [
                    x.replace("input=", "")
                    .replace("\\", "")
                    .replace('"', "")
                    .split(",")
                    for x in raster_info
                    if x.startswith("input=")
                ][0]
                rm_rasters.extend(dtm_rasters)
        # check if nDSM has to be computed
        if ndsm_out is None and dsm_out and dtm_out:
            ndsm_out = f"ndsm_{fs}_{ID}"
            compute_ndsm(dtm_out, dsm_out, ndsm_out)
        if ndsm_out:
            ndsm_list.append(ndsm_out)

    # create VRT
    if len(ndsm_list) > 0:
        create_vrt(ndsm_list, output)
        # chechk result for completness
        check_completeness_of_ndsm(aoi, output)
    else:
        grass.fatal(_("No nDSM imported!"))
    grass.message(_(f"nDSM raster map <{output}> is created."))


if __name__ == "__main__":
    options, flags = grass.parser()
    atexit.register(cleanup)
    main()
