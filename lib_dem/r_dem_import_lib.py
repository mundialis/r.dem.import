#!/usr/bin/env python3
#
############################################################################
#
# MODULE:      r_dem_import_lib
# AUTHOR(S):   Anika Weinmann
#
# PURPOSE:     Library for r.dem.import
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

OPEN_DATA_AVAILABILITY = {
    "DTM": {
        "NO_OPEN_DATA": ["BW", "BY"],
        "NOT_YET_SUPPORTED": [
            # available data
            "RP",
            "ST",
            # no data available
            "MV",
            "NI",
            "SL",
            "SH",
        ],
        "SUPPORTED": [
            "BB",
            "BE",
            "HE",
            "HH",
            "NW",
            "SN",
            "TH",
        ],
    },
    "DSM": {
        "NO_OPEN_DATA": ["BW", "BY"],
        "NOT_YET_SUPPORTED": [
            # available data
            "NW",
            "ST",
            # no data available
            "MV",
            "NI",
            "RP",
            "SH",
            "SL",
        ],
        "SUPPORTED": [
            "BB",
            "BE",
            "HE",
            "HH",
            "SN",
            "TH",
        ],
    },
    "nDSM": {
        "NO_OPEN_DATA": ["BW", "BY"],
        "NOT_YET_SUPPORTED": [
            # calculated
            "BB",
            "BE",
            "HE",
            "HH",
            "TH",
            # available data
            "SN",
            "ST",
            # no data available
            "MV",
            "NI",
            "RP",
            "SH",
            "SL",
        ],
        "SUPPORTED": [
            "NW",
        ],
    },
}
