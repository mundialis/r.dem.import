#!/usr/bin/env python3
#
############################################################################
#
# MODULE:      r.ndsm.import test Brandenburg and Sachsen
# AUTHOR(S):   Anika Weinmann

# PURPOSE:     Tests r.ndsm.import Brandenburg and Sachsen
# COPYRIGHT:   (C) 2024 by mundialis GmbH & Co. KG and the GRASS Development
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
import grass.script as grass
from r_ndsm_import_test_base import RImportNdsmTestBase


class TestRNdsmImportBBSN(RImportNdsmTestBase):
    """Test class for r.ndsm.import for BB and SN"""

    fs = "BB,SN"
    ref_res = 0.2
    num_rast_regext = 7
    num_rast_aoi = 3
    rm_rast_pattern = ["dom1_*", "dgm1_*", "ndsm_*"]

    def test_region_extent_for_output(self):
        """
        If no aoi is given the output map extent should be as big as the region
        """
        grass.run_command("g.region", vector=self.aoi_map, res=1, flags="a")
        self.region_extent_for_output()

    def test_aoi_extent_for_output(self):
        """
        The output map extent should have the same extent as the aoi
        """
        self.aoi_extent_for_output()


if __name__ == "__main__":
    test()
