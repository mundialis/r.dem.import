#!/usr/bin/env python3
#
############################################################################
#
# MODULE:      r.ndsm.import test Nordrhein-Westfalen
# AUTHOR(S):   Veronica Koess, Anika Weinmann

# PURPOSE:     Tests r.ndsm.import Nordrhein-Westfalen
# COPYRIGHT:   (C) 2023 by mundialis GmbH & Co. KG and the GRASS Development
#              Team
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

from grass.gunittest.main import test
from r_ndsm_import_test_base import RImportNdsmTestBase


class TestRNdsmImportNW(RImportNdsmTestBase):
    """Test class for r.ndsm.import for NW"""

    fs = "NW"
    ref_res = 0.5
    num_rast_regext = 1
    num_rast_aoi = 3
    rm_rast_pattern = ["ndom50*"]

    def test_region_extent_for_output(self):
        """
        If no aoi is given the output map extent should be as big as the region
        """
        self.region_extent_for_output()

    def test_aoi_extent_for_output(self):
        """
        The output map extent should have the same extent as the aoi
        """
        self.aoi_extent_for_output()


if __name__ == "__main__":
    test()
