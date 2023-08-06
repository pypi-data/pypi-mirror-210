# -*- coding=utf-8 -*-

"""Khloraa scaffolding library."""

from typing import Literal


# DOCU main documentation and docstrings
# DOCU remove region codes
# ============================================================================ #
#                                     TYPES                                    #
# ============================================================================ #
RegionIDT = Literal['sc', 'ir', 'dr']


# ============================================================================ #
#                                   CONSTANTS                                  #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                              Region Identifiers                              #
# ---------------------------------------------------------------------------- #
SC_REGION_ID: RegionIDT = 'sc'
"""Single copy region identifier."""

IR_REGION_ID: RegionIDT = 'ir'
"""Inverted repeat identifier."""

DR_REGION_ID: RegionIDT = 'dr'
"""Direct repeat identifier."""
