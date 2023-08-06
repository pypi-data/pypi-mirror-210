# -*- coding=utf-8 -*-

"""Output of scaffolding subcommand."""

from datetime import datetime
from pathlib import Path
from typing import Iterable, Iterator, Literal, Optional

from revsymg.index_lib import IndexT, IndOrT, OrT

from khloraascaf.inputs import (
    FORWARD_STR,
    REVERSE_STR,
    STR_ORIENT,
    IdCT,
    OrStrT,
)
from khloraascaf.lib import RegionIDT
from khloraascaf.multiplied_doubled_contig_graph import (
    CIND_IND,
    COR_IND,
    MDCGraphIDContainer,
)
from khloraascaf.result import ScaffoldingResult


# DOCU missing docstrings for constants
# ============================================================================ #
#                                     TYPES                                    #
# ============================================================================ #
OrCT = tuple[IdCT, OrT]
"""
Oriented contig type.

:alias of: :class:`tuple` (:class:`IdCT`, :class:`IndexT`)
"""
# DOCU any role cannot find IndexT
# ============================================================================ #
#                                   CONSTANTS                                  #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                                 For OrCT Type                                #
# ---------------------------------------------------------------------------- #
ORC_ID_IND: Literal[0] = 0
"""Index of the identifier for :class:`~revsymg.index_lib.OrT`"""
ORC_OR_IND: Literal[1] = 1
"""Index of the orientation for :class:`~revsymg.index_lib.OrT`"""

# ---------------------------------------------------------------------------- #
#                                 Orientations                                 #
# ---------------------------------------------------------------------------- #
ORIENT_INT_STR: tuple[OrStrT, OrStrT] = (FORWARD_STR, REVERSE_STR)
"""Get orientation strings from orientation binaries.

:type: :class:`tuple` (:class:`str`, :class:`str`)
"""

# ---------------------------------------------------------------------------- #
#                                     Files                                    #
# ---------------------------------------------------------------------------- #
#
# Contigs of the Regions
#
CONTIGS_OF_REGIONS_PREFIX = 'contigs_of_regions'
"""Prefix of the contigs of regions file name."""
CONTIGS_OF_REGIONS_EXT = 'tsv'
"""Extension of the contigs of regions file"""
#
# Map of the regions
#
MAP_OF_REGIONS_PREFIX = 'map_of_regions'
"""Prefix of the map of regions file name."""
MAP_OF_REGIONS_EXT = 'tsv'
"""Extension of the map of regions file"""


# ============================================================================ #
#                                   FUNCTIONS                                  #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                          Default Output Directories                          #
# ---------------------------------------------------------------------------- #
def generate_output_directory(instance_name: str) -> Path:
    """Return an single copy output directory path.

    The output directory name respects the following format:
    ``<yyyy>-<mm>-<dd>_<HH>:<MM>:<SS>_<instance_name>``

    Parameters
    ----------
    instance_name : str
        Instance's name

    Returns
    -------
    Path
        Output directory
    """
    # DOCU output directory generated function
    return Path(
        datetime.now().strftime('%Y-%m-%d_%H:%M:%S') + '_' + instance_name,
    )


# ---------------------------------------------------------------------------- #
#                              Contigs Of Regions                              #
# ---------------------------------------------------------------------------- #
def write_contigs_of_regions(
        result: ScaffoldingResult, contigs_of_regions_path: Path,
        id_container: Optional[MDCGraphIDContainer] = None):
    """Write the regions' contigs file.

    #DOCU describe the output file here

    Parameters
    ----------
    result : ScaffoldingResult
        Previous scaffolding result
    contigs_of_regions_path : Path
        Path of the future file containing the regions' oriented contigs
    id_container : MDCGraphIDContainer, optional
        Identifiers container for the graph, by default None
    """
    # TOTEST function needs ScaffoldingResult & MDCGraphIDContainer fixtures
    with open(contigs_of_regions_path, 'w', encoding='utf-8') as f_out:
        for region_index in range(result.number_regions()):
            line: str = ''
            for occorc in result.region_occorc(region_index):
                if id_container is not None:
                    line += str(
                        id_container.vertex_to_contig(occorc[CIND_IND]),
                    ) + '\t'
                else:
                    line += f'\t{occorc[CIND_IND]}'
                line += f'{ORIENT_INT_STR[occorc[COR_IND]]}\t'
            f_out.write(line[:-1] + '\n')


def read_contigs_of_regions(contigs_of_regions_path: Path) -> (
        Iterator[tuple[OrCT, ...]]):
    """Read the regions' contigs file.

    Parameters
    ----------
    contigs_of_regions_path : Path
        List of oriented contigs for each region

    Yields
    ------
    tuple of OrCT
        List of oriented contigs for one region
    """
    with open(contigs_of_regions_path, 'r', encoding='utf-8') as cor_in:
        for line in cor_in:
            orc_of_region: list[OrCT] = []
            l_orc = line.split()
            k = 0
            while k < len(l_orc) - 1:
                orc_of_region.append(
                    (l_orc[k], STR_ORIENT[l_orc[k + 1]]),  # type: ignore
                )
                k += 2
            yield tuple(orc_of_region)


def fmt_contigs_of_regions_filename(
        instance_name: str, ilp_combination: Iterable[RegionIDT]) -> str:
    """Format the contigs of regions filename.

    Parameters
    ----------
    instance_name : str
        Instance name
    ilp_combination : iterable of RegionIDT
        ILP string code combination

    Returns
    -------
    str
        Formatted filename
    """
    return (
        f'{CONTIGS_OF_REGIONS_PREFIX}_{instance_name}'
        f"_{'_'.join(ilp_combination)}"
        f'.{CONTIGS_OF_REGIONS_EXT}'
    )


# ---------------------------------------------------------------------------- #
#                                Map Of Regions                                #
# ---------------------------------------------------------------------------- #
def write_map_of_regions(result: ScaffoldingResult,
                         map_of_regions_path: Path):
    """Write the region map file.

    # DOCU describe the output file here

    Parameters
    ----------
    result : ScaffoldingResult
        Scaffolding result
    map_of_regions_path : Path
        Path of the future file containing the regions' oriented contigs
    """
    with open(map_of_regions_path, 'w', encoding='utf-8') as f_out:
        for reg_ind, reg_or in result.map_of_regions():
            f_out.write(f'{reg_ind}\t{ORIENT_INT_STR[reg_or]}\n')


def read_map_of_regions(map_of_regions_path: Path) -> Iterator[IndOrT]:
    """Write the region map file.

    Parameters
    ----------
    map_of_regions_path : Path
        Map of regions

    Yields
    ------
    IndOrT
        The index and the orientation of the region
    """
    with open(map_of_regions_path, 'r', encoding='utf-8') as mof_in:
        for line in mof_in:
            reg_indstr, reg_orstr = line.split()
            yield IndexT(reg_indstr), STR_ORIENT[reg_orstr]  # type: ignore


def fmt_map_of_regions_filename(
        instance_name: str, ilp_combination: Iterable[RegionIDT]) -> str:
    """Format map of the regions filename.

    Parameters
    ----------
    instance_name : str
        Instance name
    ilp_combination : iterable of str
        ILP string code combination

    Returns
    -------
    str
        Formatted filename
    """
    return (
        f'{MAP_OF_REGIONS_PREFIX}_{instance_name}'
        f"_{'_'.join(ilp_combination)}"
        f'.{MAP_OF_REGIONS_EXT}'
    )
