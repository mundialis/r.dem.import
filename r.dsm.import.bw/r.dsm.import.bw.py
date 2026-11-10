#!/usr/bin/env python3
#
############################################################################
#
# MODULE:      r.dsm.import.bw
# AUTHOR(S):   Kim Kaiser, Veronica Koess, Anika Weinmann
# PURPOSE:     Downloads DSM for Baden-Württemberg
# SPDX-FileCopyrightText: (c) 2026 by mundialis GmbH & Co. KG and the
#                             GRASS Development Team
# SPDX-License-Identifier: GPL-3.0-or-later.
#
############################################################################

# %module
# % description: Downloads DSM for Baden-Württemberg and aoi.
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

import grass.script as grass
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
from osgeo import gdal

# set variables
TINDEX = (
    "https://github.com/mundialis/tile-indices/raw/main/DSM/BW/"
    "BW_DSM_tindex_proj.gpkg.gz"
)
CURRENT_WORKING_DIR = pathlib.Path.cwd()
ID = grass.tempname(12)
ORIG_REGION = f"original_region_{ID}"

keep_data = False
download_dir = None
rm_rasters = []
rm_vectors = []


def skip_extra_tiles(filepath, filename):
    """Every Tindex tile contains the download URL to one ZIP folder.
    These folders contain multiple smaller tiles. The import for tiles not
    matching the AOI will be skipped.

    Args:
        filepath (str): gdal path to TIFF file
        filename(str): Name of tested TIFF file without extension

    """

    # Get current region extent
    region = grass.region()

    # Get raster extent
    ds = gdal.Open(str(filepath))
    gt = ds.GetGeoTransform()
    corners = [
        gdal.ApplyGeoTransform(gt, x, y)
        for x, y in [
            (0, 0),
            (ds.RasterXSize, 0),
            (0, ds.RasterYSize),
            (ds.RasterXSize, ds.RasterYSize),
        ]
    ]
    raster_w = min(p[0] for p in corners)
    raster_e = max(p[0] for p in corners)
    raster_s = min(p[1] for p in corners)
    raster_n = max(p[1] for p in corners)
    ds = None

    # Check if raster overlaps with AOI
    if (
        raster_e <= region["w"]
        or raster_w >= region["e"]
        or raster_n <= region["s"]
        or raster_s >= region["n"]
    ):
        grass.message(_("Skipping {}: no overlap with AOI").format(filename))
        return False
    return True


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
    """Main function of r.dsm.import.bw."""
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
    tindex_vect = f"dsm_tindex_{ID}"
    rm_vectors.append(tindex_vect)
    download_and_import_tindex(TINDEX, tindex_vect, download_dir)

    # get download urls which overlap with aoi
    url_tiles = get_list_of_tindex_locations(tindex_vect, aoi)

    # import DSMs directly
    grass.message(_(f"Importing {len(url_tiles)} DSMs..."))
    all_dsms = []
    for url in url_tiles:
        zip_url = f"/vsizip//vsicurl/{url}"

        # get ZIP directory
        zip_dirs = gdal.ReadDir(zip_url)
        for zip_dir in zip_dirs:
            subdir = f"{zip_url}/{zip_dir}"

        # get TIFF files
        files = gdal.ReadDir(subdir)
        tiff_files = [item for item in files if ".tif" in item]
        for tiff_file in tiff_files:
            tiff_path = f"{subdir}/{tiff_file}"
            tiff_filename = pathlib.Path(tiff_file).stem
            if aoi:
                grass.run_command("g.region", vector=aoi)
            else:
                grass.run_command("g.region", region=ORIG_REGION)
            grass.run_command("g.region", res=1, grow=1, quiet=True)

            # skip files not matching aoi
            if skip_extra_tiles(tiff_path, tiff_filename):
                tiff_tmp = f"tmp_{tiff_filename}"

                # currently DSM tifs are given with COMPOUNDCRS
                # with PROJCRS: 25832 and VERTCRS: 7837 (for vertical data)
                # r.import check of CRS yields error, even in 25832 projection.
                # Therefore gdal.Warp is used for reprojection.
                gdal.Warp(
                    srcDSOrSrcDSTab=str(tiff_path),
                    destNameOrDestDS=tiff_tmp,
                    dstSRS="EPSG:25832",
                )

                # import TIFF files
                grass.run_command(
                    "r.import",
                    input=tiff_tmp,
                    output=tiff_filename,
                    extent="region",
                    overwrite=True,
                    quiet=True,
                )
                rm_rasters.append(tiff_tmp)
                all_dsms.append(tiff_filename)

    # create VRT of tiles
    # (dont copy raster maps -> create real raster in the next steps)
    vrt = f"vrt_dsm_{output}_{ID}"
    rm_rasters.append(vrt)
    rm_rasters.extend(all_dsms)
    create_vrt(all_dsms, vrt, copy_raster_maps=False)

    # resample/interpolate whole VRT (because interpolating single files leads
    # to empty rows and columns)
    # check resolution and resample / interpolate data if needed
    if not native_res:
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

    grass.message(_(f"DSM raster map <{output}> is created."))

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
