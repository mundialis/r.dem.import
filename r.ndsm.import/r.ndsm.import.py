#!/usr/bin/env python3
#
############################################################################
#
# MODULE:      r.ndsm.import
# AUTHOR(S):   Anika Weinmann, Kim Kaiser, Veronica Koess, Leon Louwarts
# PURPOSE:     Downloads (image based) digital surface models (iDSM/DSM) and
#              digital terrain models (DTM) for specified federal state and
#              area of interest, and creates a single file of a normalised
#              DSM (nDSM) in GRASS.
# SPDX-FileCopyrightText: (c) 2026 by mundialis GmbH & Co. KG and the
#                             GRASS Development Team
# SPDX-License-Identifier: GPL-3.0-or-later.
#
############################################################################

# %module
# % description: Downloads DSM and DTM for specified federal state and aoi and creates a single file of a normalised DSM.
# % keyword: raster
# % keyword: import
# % keyword: nDSM
# % keyword: nDOM
# % keyword: DOM
# % keyword: iDSM
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
# % key: local_data_dir_idsm
# % required: no
# % description: Directory with raster map of iDSMs to import (e.g. VRT)
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
# % excludes: -r,alignment_raster
# %end

import atexit
import os
import sys

import grass.script as grass
from grass.pygrass.utils import get_lib_path

from grass_gis_helpers.cleanup import general_cleanup
from grass_gis_helpers.data_import import import_local_raster_data
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
    from r_dem_import_lib import (
        OPEN_DATA_AVAILABILITY,
        import_local_data,
    )
    from r_dem_import_metadata_lib import get_download_urls_and_names
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


def compute_ndsm(dtm, idsm, dsm, ndsm):
    """Compute nDSM out of DTM and DSM

    Args:
        dtm (str): Name of DTM input raster map
        idsm (str): Name of iDSM input raster map
        dsm (str): Name of DSM input raster map
        ndsm (str): Name for output nDSM raster map
    """
    # use iDSM if given, otherwise use DSM
    if idsm:
        grass.run_command("g.region", raster=idsm)
        grass.run_command(
            "r.mapcalc",
            expression=f"{ndsm} = {idsm} - {dtm}",
            quiet=True,
        )
    else:
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


def get_addon_name(fs):
    """Function to get the addon name for the function to get license info"""
    return f"r.ndsm.import.{fs.lower()}"


def main():
    """Main function of r.ndsm.import"""
    global rm_rasters

    aoi = options["aoi"]
    federal_states = get_federal_states(
        options["federal_state"], options["federal_state_file"]
    )
    local_data_dir_ndsm = options["local_data_dir_ndsm"]
    local_data_dir_idsm = options["local_data_dir_idsm"]
    local_data_dir_dsm = options["local_data_dir_dsm"]
    local_data_dir_dtm = options["local_data_dir_dtm"]
    download_dir = check_download_dir(options["download_dir"])
    alignment_raster = options["alignment_raster"]
    metadata_path = options["metadata"]
    output = options["output"]
    keep_data = flags["k"]
    nativ_res = flags["r"]

    # save orig region
    grass.run_command("g.region", save=ORIG_REGION, quiet=True)

    # local nDSM files
    local_ndsm_fs_list = []
    if local_data_dir_ndsm and local_data_dir_ndsm != "":
        local_ndsm_fs_list = os.listdir(local_data_dir_ndsm)

    # local iDSM files
    local_idsm_fs_list = []
    if local_data_dir_idsm and local_data_dir_idsm != "":
        grass.fatal(_("Local iDSM data dir for nDSM is not yet supported."))
        local_idsm_fs_list = os.listdir(local_data_dir_idsm)

    # local DSM files
    local_dsm_fs_list = []
    if local_data_dir_dsm and local_data_dir_dsm != "":
        grass.fatal(_("Local DSM data dir for nDSM is not yet supported."))
        local_dsm_fs_list = os.listdir(local_data_dir_dsm)

    # local DTM files
    local_dtm_fs_list = []
    if local_data_dir_dtm and local_data_dir_dtm != "":
        grass.fatal(_("Local DTM data dir for nDSM is not yet supported."))
        local_dtm_fs_list = os.listdir(local_data_dir_dtm)

    ndsm_list = []
    metadata_list = []
    for fs in federal_states:
        grass.run_command("g.region", region=ORIG_REGION)
        ndsm_out = None
        dtm_out = None
        idsm_out = None
        dsm_out = None
        # check if local data for federal state given
        imported_local_data = False
        if fs in local_ndsm_fs_list:
            grass.message(_("Local nDSM import not yet supported!"))
            imported_local_data = import_local_data(
                aoi,
                output,
                local_data_dir_ndsm,
                fs,
                ndsm_list,
                rm_rasters,
                "raster",
                nativ_res,
            )
        # TODO import nDSM via local iDSM/DSM and DTM
        # elif fs in OPEN_DATA_AVAILABILITY["nDSM"]["NO_OPEN_DATA"]:
        #     grass.fatal(
        #         _(f"No local data for {fs} available. Is the path correct?")
        #     )

        # set flags for nDSM, iDSM, DSM and DTM
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
            ndsm_metadata_tmpfile = None
            if metadata_path:
                ndsm_metadata_tmpfile = grass.tempfile()

            grass.run_command(
                f"r.ndsm.import.{fs.lower()}",
                aoi=aoi,
                download_dir=os.path.join(download_dir, "nDSM"),
                alignment_raster=alignment_raster,
                output=ndsm_out,
                flags=import_flags,
                metadata_file=ndsm_metadata_tmpfile,
                quiet=True,
                overwrite=True,
            )
            if ndsm_metadata_tmpfile:
                ndsm_urls, ndsm_names = get_download_urls_and_names(
                    metadata_tmpfile=ndsm_metadata_tmpfile,
                    keep_data=keep_data,
                    download_dir=os.path.join(download_dir, "nDSM"),
                    out_fs=ndsm_out,
                    fs=fs,
                )
                license_info, base_url = get_license_and_url_from_addon(
                    f"r.ndsm.import.{fs.lower()}"
                )
                metadata_list.append(
                    collect_metadata(
                        fs=fs,
                        raster_list=[ndsm_out],
                        license_info=license_info,
                        base_url=base_url,
                        original_names=ndsm_names,
                        download_urls=ndsm_urls,
                    )
                )

        # import iDSM data
        if (
            imported_local_data is False
            and (
                fs in local_idsm_fs_list
                or fs in OPEN_DATA_AVAILABILITY["iDSM"]["SUPPORTED"]
            )
        ) and ndsm_out is None:
            grass.message(_(f"Importing iDSM data for {fs}..."))
            idsm_out = f"idsm_{fs}_{ID}"
            rm_rasters.append(idsm_out)
            idsm_metadata_tmpfile = None
            if metadata_path:
                idsm_metadata_tmpfile = grass.tempfile()

            grass.run_command(
                "r.idsm.import",
                aoi=aoi,
                federal_state=fs,
                local_data_dir=local_data_dir_idsm,
                download_dir=os.path.join(download_dir, "iDSM"),
                alignment_raster=alignment_raster,
                output=idsm_out,
                flags=import_flags,
                metadata_file=idsm_metadata_tmpfile,
                quiet=True,
            )
            if idsm_metadata_tmpfile:
                idsm_urls, idsm_names = get_download_urls_and_names(
                    metadata_tmpfile=idsm_metadata_tmpfile,
                    keep_data=keep_data,
                    download_dir=os.path.join(download_dir, "iDSM"),
                    out_fs=idsm_out,
                    fs=fs,
                )
                license_info, base_url = get_license_and_url_from_addon(
                    f"r.idsm.import.{fs.lower()}"
                )
                metadata_list.append(
                    collect_metadata(
                        fs=fs,
                        raster_list=[idsm_out],
                        license_info=license_info,
                        base_url=base_url,
                        original_names=idsm_names,
                        download_urls=idsm_urls,
                    )
                )
            raster_info = grass.raster_info(idsm_out)["comments"].split()
            if raster_info[0].replace('"', "") in ["r.buildvrt", "r.patch"]:
                idsm_rasters = [
                    x.replace("input=", "")
                    .replace("\\", "")
                    .replace('"', "")
                    .split(",")
                    for x in raster_info
                    if x.startswith("input=")
                ][0]
                rm_rasters.extend(idsm_rasters)
        else:
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
                dsm_metadata_tmpfile = None
                if metadata_path:
                    dsm_metadata_tmpfile = grass.tempfile()

                grass.run_command(
                    "r.dsm.import",
                    aoi=aoi,
                    federal_state=fs,
                    local_data_dir=local_data_dir_dsm,
                    download_dir=os.path.join(download_dir, "DSM"),
                    alignment_raster=alignment_raster,
                    output=dsm_out,
                    flags=import_flags,
                    metadata_file=dsm_metadata_tmpfile,
                    quiet=True,
                )
                if dsm_metadata_tmpfile:
                    dsm_urls, dsm_names = get_download_urls_and_names(
                        metadata_tmpfile=dsm_metadata_tmpfile,
                        keep_data=keep_data,
                        download_dir=os.path.join(download_dir, "DSM"),
                        out_fs=dsm_out,
                        fs=fs,
                    )
                    license_info, base_url = get_license_and_url_from_addon(
                        f"r.dsm.import.{fs.lower()}"
                    )
                    metadata_list.append(
                        collect_metadata(
                            fs=fs,
                            raster_list=[dsm_out],
                            license_info=license_info,
                            base_url=base_url,
                            original_names=dsm_names,
                            download_urls=dsm_urls,
                        )
                    )
                raster_info = grass.raster_info(dsm_out)["comments"].split()
                if raster_info[0].replace('"', "") in [
                    "r.buildvrt",
                    "r.patch",
                ]:
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
            dtm_metadata_tmpfile = None
            if metadata_path:
                dtm_metadata_tmpfile = grass.tempfile()

            grass.run_command(
                "r.dtm.import",
                aoi=aoi,
                federal_state=fs,
                local_data_dir=local_data_dir_dtm,
                download_dir=os.path.join(download_dir, "DTM"),
                alignment_raster=alignment_raster,
                output=dtm_out,
                flags=import_flags,
                metadata_file=dtm_metadata_tmpfile,
                quiet=True,
            )
            if dtm_metadata_tmpfile:
                dtm_urls, dtm_names = get_download_urls_and_names(
                    metadata_tmpfile=dtm_metadata_tmpfile,
                    keep_data=keep_data,
                    download_dir=os.path.join(download_dir, "DTM"),
                    out_fs=dtm_out,
                    fs=fs,
                )
                license_info, base_url = get_license_and_url_from_addon(
                    f"r.dtm.import.{fs.lower()}"
                )
                metadata_list.append(
                    collect_metadata(
                        fs=fs,
                        raster_list=[dtm_out],
                        license_info=license_info,
                        base_url=base_url,
                        original_names=dtm_names,
                        download_urls=dtm_urls,
                    )
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
        if ndsm_out is None:
            ndsm_out = f"ndsm_{fs}_{ID}"
            compute_ndsm(dtm_out, idsm_out, dsm_out, ndsm_out)
        ndsm_list.append(ndsm_out)

    # Patch nDSMs of different federal states
    # (keep as VRT. Federal states nDSMs itself are no VRTs)
    if len(ndsm_list) > 0:
        create_vrt(ndsm_list, output)
        # check result for completeness
        check_completeness_of_ndsm(aoi, output)
    else:
        grass.fatal(_("No nDSM imported!"))
    grass.message(_(f"nDSM raster map <{output}> is created."))

    # Write metadata file if metadata_path was set
    write_metadata_markdown(
        metadata_list=metadata_list,
        metadata_path=metadata_path,
        data_label="nDOM",
    )


if __name__ == "__main__":
    options, flags = grass.parser()
    atexit.register(cleanup)
    main()
