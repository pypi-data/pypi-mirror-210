# -*- coding=utf-8 -*-

"""Input data module."""

from pathlib import Path
from typing import Iterator, Literal

from revsymg.index_lib import FORWARD_INT, REVERSE_INT, OrT


# DOCU types, constants and functions
# ============================================================================ #
#                                     TYPES                                    #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                                    Contigs                                   #
# ---------------------------------------------------------------------------- #
IdCT = str
"""Contig ID type."""

MultT = int
"""Multiplicity type."""

PresScoreT = float
"""Contig's presence score type."""

# ---------------------------------------------------------------------------- #
#                                     Links                                    #
# ---------------------------------------------------------------------------- #
IdLT = str
"""Link ID type."""

OrStrT = Literal['-', '+']
"""Orientation type for link strings."""

LinkStrT = tuple[IdLT, IdCT, OrStrT, IdCT, OrStrT]
"""Link strings type."""

LinkT = tuple[IdLT, IdCT, OrT, IdCT, OrT]
"""Link type."""

# ============================================================================ #
#                                   CONSTANTS                                  #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                                    Solvers                                   #
# ---------------------------------------------------------------------------- #
SOLVER_CBC = 'cbc'
SOLVER_GUROBI = 'gurobi'

# ---------------------------------------------------------------------------- #
#                                Default Values                                #
# ---------------------------------------------------------------------------- #
# DOCU docstrings for default values
MULT_UPB_DEF = 4
"""
"""

PRESSCORE_UPB_DEF = 1.0
OUTDEBUG_DEF = False
OUTDIR_DEF = Path('./')
INSTANCE_NAME_DEF = 'khloraascaf'

# ---------------------------------------------------------------------------- #
#                                 Contigs Links                                #
# ---------------------------------------------------------------------------- #
#
# Orientation strings
#
FORWARD_STR: OrStrT = '+'
REVERSE_STR: OrStrT = '-'

STR_ORIENT: dict[OrStrT, OrT] = {
    FORWARD_STR: FORWARD_INT,
    REVERSE_STR: REVERSE_INT,
}


# ============================================================================ #
#                                   FUNCTIONS                                  #
# ============================================================================ #
def read_contig_attributes(
        contig_attrs_path: Path) -> Iterator[tuple[IdCT, MultT, PresScoreT]]:
    """Iterate over contigs attributes.

    Parameters
    ----------
    contig_attrs_path : Path
        Contigs attributes filepath

    Yields
    ------
    IdCT
        Contig's identifier
    MultT
        Contig's multiplicity
    PresScoreT
        Contig's presence score
    """
    with open(contig_attrs_path, 'r', encoding='utf-8') as cattrs_fin:
        for line in cattrs_fin:
            split_line = line.split()
            if split_line:
                contig_id, mult_str, presscore_str = split_line
                yield contig_id, MultT(mult_str), PresScoreT(presscore_str)


def read_contig_links_file(contig_links_path: Path) -> Iterator[LinkT]:
    """Iterate over contigs links.

    Parameters
    ----------
    contig_links_path : Path
        Contigs liniks filepath

    Yields
    ------
    IdCT
        Link's identifier
    IdCT
        Fisrt contig's identifier
    OrT
        First contig's orientation
    IdCT
        Second contig's identifier
    OrT
        Second contig's orientation
    """
    with open(contig_links_path, 'r', encoding='utf-8') as clinks_fin:
        for line in clinks_fin:
            l_id, c_id, c_or_str, d_id, d_or_str = line.split()

            yield (
                l_id,
                c_id, STR_ORIENT[c_or_str],  # type: ignore
                d_id, STR_ORIENT[d_or_str],  # type: ignore
            )
