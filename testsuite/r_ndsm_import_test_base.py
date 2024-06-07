#!/usr/bin/env python3
#
############################################################################
#
# MODULE:      r.ndsm.import test
# AUTHOR(S):   Veronica Köß, Johannes Halbauer, Anika Weinmann
# PURPOSE:     Test base for r.ndsm.import
# COPYRIGHT:   (C) 2022-2024 by mundialis GmbH & Co. KG and the GRASS
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
#############################################################################

import os

from grass.gunittest.case import TestCase
from grass.gunittest.gmodules import SimpleModule
import grass.script as grass

from grass_gis_helpers.cleanup import cleaning_tmp_location
from grass_gis_helpers.location import (
    create_tmp_location,
    get_current_location,
)
from grass_gis_helpers.tests import (
    check_number_of_grass_elements,
    get_number_of_grass_elements,
)


class RImportNdsmTestBase(TestCase):
    """Base test class for r.ndsm.import"""

    fs = ""
    ref_res = None
    pid = os.getpid()
    test_polygon = f"temp_test_{pid}"
    test_output = f"output_{pid}"
    aoi_map = f"aoi_map_{pid}"
    orig_region = f"orig_region{pid}"

    rm_vec = []
    rm_vec.append(aoi_map)
    rm_rast_pattern = []
    num_rast_regext = 1
    num_rast_aoi = 1

    ORIG_GISRC = None
    TMP_LOC = None
    GISDBASE = None
    TMP_GISRC = None

    # pylint: disable=invalid-name
    def tearDown(self):
        """Tear Down method to remove created vector and raster maps"""
        self.runModule("g.remove", type="vector", name="rm_vec", flags="f")
        self.rm_rast_pattern.append(f"{self.test_output}*")
        for rast_pattern in self.rm_rast_pattern:
            self.runModule(
                "g.remove",
                type="raster",
                pattern=rast_pattern,
                flags="f",
            )

    @classmethod
    # pylint: disable=invalid-name
    def tearDownClass(cls):
        """Tear down class method to remove and reset region and remove
        temporary location"""
        if cls.fs != "":
            grass.run_command("g.region", region=cls.orig_region)
            grass.run_command(
                "g.remove", type="region", name=cls.orig_region, flags="f"
            )
            # switch location and remove temp location
            cleaning_tmp_location(
                cls.ORIG_GISRC, cls.TMP_LOC, cls.GISDBASE, cls.TMP_GISRC
            )

    @classmethod
    # pylint: disable=invalid-name
    def setUpClass(cls):
        """Set up class method to create temporary location, import area of
        interest and set region"""
        if cls.fs != "":
            # switch to location with EPSG code 25832
            loc, mapset, cls.GISDBASE, cls.ORIG_GISRC = get_current_location()
            if cls.TMP_LOC is None:
                cls.TMP_LOC, cls.TMP_GISRC = create_tmp_location(epsg=25832)
            # import aoi_map for testing
            fs = cls.fs.replace(",", "_")
            cls.runModule(
                "v.import",
                input=os.path.join("data", f"test_aoi_{fs}.gpkg"),
                output=cls.aoi_map,
                overwrite=True,
            )
            # set region
            grass.run_command("g.region", save=cls.orig_region)
            grass.run_command("g.region", vector=cls.aoi_map, flags="a")
            grass.run_command("g.region", n="n+200", s="n-100", w="e-100")

    def check_extension_map(self, type="vector", aoi=None):
        """Method to check the extension of the output vector map
        and the region or aoi

        Args:
            type (str): The type of map for which the extension should be
                        checked "vector" or "raster"
            aoi (str): Name of the area of interest vectormap; if no one is set
                       the current region is used
        """
        if not aoi:
            reg = grass.region()
            ext_aoi_n = float(reg["n"])
            ext_aoi_s = float(reg["s"])
            ext_aoi_e = float(reg["e"])
            ext_aoi_w = float(reg["w"])
        else:
            aoi_reg = grass.parse_command("v.info", map=aoi, flags="g")
            ext_aoi_n = float(aoi_reg["north"])
            ext_aoi_s = float(aoi_reg["south"])
            ext_aoi_e = float(aoi_reg["east"])
            ext_aoi_w = float(aoi_reg["west"])

        # get extent of output vector map
        if type == "vector":
            out_reg = grass.parse_command(
                "v.info", map=self.test_output, flags="g"
            )
        else:
            out_reg = grass.parse_command(
                "r.info", map=self.test_output, flags="g"
            )
        ext_out_n = float(out_reg["north"])
        ext_out_s = float(out_reg["south"])
        ext_out_e = float(out_reg["east"])
        ext_out_w = float(out_reg["west"])

        # use rounded floats to prevent error caused by different last digits
        self.assertTrue(
            ext_aoi_n <= ext_out_n
            and ext_aoi_s >= ext_out_s
            and ext_aoi_e <= ext_out_e
            and ext_aoi_w >= ext_out_w,
            "Respective extents of given aoi and output map are equal.",
        )

    def check_raster_res(self, ref_res):
        """Check the resolution of the output raster map

        Args:
            ref_res (float): The reference resolution for comparison
        """
        r_info = grass.parse_command("r.info", map=self.test_output, flags="g")
        out_res_ns = round(float(r_info["nsres"]), 2)
        out_res_ew = round(float(r_info["ewres"]), 2)
        self.assertTrue(
            ((out_res_ns == ref_res) and (out_res_ew == ref_res)),
            "Resolution of DSMs is not as expected."
            f"Expected res of {ref_res}, but got nsres of {out_res_ns}"
            f" and ewres of {out_res_ew}",
        )

    def region_extent_for_output(self):
        """
        If no aoi is given the output map extent should be as big as the region
        """
        print(f"Running test import for region for {self.fs}...")

        n_rast, n_vect, n_gr, n_reg, n_mapsets = get_number_of_grass_elements()
        check_output = SimpleModule(
            "r.ndsm.import",
            output=self.test_output,
            federal_state=self.fs.split(","),
            overwrite=True,
        )
        self.assertModule(
            check_output, "Importing data for the region extent failed"
        )
        self.assertRasterExists(
            self.test_output, f"Creation of {self.test_output} failed."
        )
        self.check_extension_map(type="raster")
        check_number_of_grass_elements(
            n_rast + self.num_rast_regext, n_vect, n_gr, n_reg, n_mapsets
        )
        print(
            "Running test importing data for region extent of "
            f"{self.fs} finished."
        )

    def aoi_extent_for_output(self):
        """
        Tests importing data only for aoi given by aoi_map
        """
        print(f"\nTest aoi {self.fs}...")

        n_rast, n_vect, n_gr, n_reg, n_mapsets = get_number_of_grass_elements()
        check_output = SimpleModule(
            "r.ndsm.import",
            output=self.test_output,
            federal_state=self.fs.split(","),
            aoi=self.aoi_map,
            flags="r",
            overwrite=True,
        )
        self.assertModule(check_output, "Importing data for aoi fails.")
        self.assertRasterExists(
            self.test_output, f"Creation of {self.test_output} failed."
        )
        self.check_extension_map(type="raster", aoi=self.aoi_map)

        # check resolution
        self.check_raster_res(self.ref_res)
        check_number_of_grass_elements(
            n_rast + self.num_rast_aoi, n_vect, n_gr, n_reg, n_mapsets
        )
        print(
            f"Test for importing data only for aoi of {self.fs} successfully "
            "finished.\n"
        )
