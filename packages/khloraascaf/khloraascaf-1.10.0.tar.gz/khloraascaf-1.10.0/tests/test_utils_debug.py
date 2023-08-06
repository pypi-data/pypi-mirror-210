# -*- coding=utf-8 -*-

"""Unit testing for utils_debug module."""
from pathlib import Path

from revsymg.index_lib import FORWARD_INT, REVERSE_INT

from khloraascaf.inputs import INSTANCE_NAME_DEF
from khloraascaf.lib import DR_REGION_ID, IR_REGION_ID, SC_REGION_ID
from khloraascaf.utils_debug import (
    DIRF_CODE,
    fmt_found_repeated_fragments_filename,
    fmt_vertices_of_regions_filename,
    read_found_repeated_fragments,
    read_vertices_of_regions,
)


# ============================================================================ #
#                                   CONSTANTS                                  #
# ============================================================================ #
TEST_DIR: Path = Path(__file__).parent.absolute()
_TOY_DATADIR = TEST_DIR / 'data'
_IR_DR_SC_DIR = _TOY_DATADIR / 'ir_dr_sc'

_VERTICES_OF_REGION_PATH = (
    _IR_DR_SC_DIR
    / 'vertices_of_regions_khloraascaf_ir_dr_sc.tsv'
)

_REPFRAG_PATH = (
    _IR_DR_SC_DIR
    / 'repfrag_khloraascaf_ir_dr.tsv'
)


# ============================================================================ #
#                                TEST FUNCTIONS                                #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                              Vertices Of Regions                             #
# ---------------------------------------------------------------------------- #
def test_read_vertices_of_regions():
    """Test for read_vertices_of_regions."""
    assert tuple(
        read_vertices_of_regions(
            _VERTICES_OF_REGION_PATH,
        ),
    ) == (
        ((0, FORWARD_INT, 0), (1, REVERSE_INT, 0)),
        ((2, FORWARD_INT, 1), (3, REVERSE_INT, 1)),
        ((4, FORWARD_INT, 0),),
        ((5, FORWARD_INT, 0), (6, REVERSE_INT, 1), (7, REVERSE_INT, 1)),
        ((8, REVERSE_INT, 0),),
        ((9, FORWARD_INT, 0),),
    )


def test_fmt_vertices_of_regions_filename():
    """Test for fmt_vertices_of_regions_filename."""
    assert fmt_vertices_of_regions_filename(
        INSTANCE_NAME_DEF, (IR_REGION_ID, DR_REGION_ID, SC_REGION_ID),
    ) == _VERTICES_OF_REGION_PATH.name


# ---------------------------------------------------------------------------- #
#                           Found Repeated Fragments                           #
# ---------------------------------------------------------------------------- #
def test_read_found_repeated_fragments():
    """Test for read_found_repeated_fragments."""
    assert tuple(
        read_found_repeated_fragments(_REPFRAG_PATH),
    ) == (
        (DIRF_CODE, (2, FORWARD_INT, 0)),
        (DIRF_CODE, (3, REVERSE_INT, 0)),
    )


def test_fmt_found_repeated_fragments_filename():
    """Test for fmt_found_repeated_fragments_filename."""
    assert fmt_found_repeated_fragments_filename(
        INSTANCE_NAME_DEF, (IR_REGION_ID, DR_REGION_ID),
    ) == _REPFRAG_PATH.name
