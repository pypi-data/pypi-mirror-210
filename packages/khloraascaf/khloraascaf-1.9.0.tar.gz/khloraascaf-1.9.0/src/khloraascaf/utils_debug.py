# -*- coding=utf-8 -*-

"""Utilitary module for debugging."""


from pathlib import Path
from typing import Iterable, Iterator, Union

from revsymg.index_lib import IndexT

from khloraascaf.ilp.pulp_var_db import PuLPVarDirF, PuLPVarInvF
from khloraascaf.lib import RegionIDT
from khloraascaf.multiplied_doubled_contig_graph import OccOrCT
from khloraascaf.outputs import ORIENT_INT_STR, STR_ORIENT
from khloraascaf.result import ScaffoldingResult


# DOCU module debug
# ============================================================================ #
#                                   CONSTANTS                                  #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                                     Files                                    #
# ---------------------------------------------------------------------------- #
#
# Vertices of the regions
#
VERTICES_OF_REGIONS_PREFIX = 'vertices_of_regions'
"""Prefix of vertices of regions file name."""

VERTICES_OF_REGIONS_EXT = 'tsv'
"""Extension of vertices of regions file."""
#
# Repeated fragments
#
INVF_CODE = 'invf'
"""Inverted fragments code."""

DIRF_CODE = 'dirf'
"""Direct fragments code."""

FOUND_REPFRAG_PREFIX = 'repfrag'
"""Prefix of found repeated fragments file name."""

FOUND_REPFRAG_EXT = 'tsv'
"""Extension of found repeated fragments file."""


# ============================================================================ #
#                                   FUNCTIONS                                  #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                              Vertices Of Regions                             #
# ---------------------------------------------------------------------------- #
def write_vertices_of_regions(result: ScaffoldingResult,
                              vertices_of_regions_path: Path):
    """Write the regions' vertex file.

    #DOCU describe the output file here

    Parameters
    ----------
    result : ScaffoldingResult
        Previous scaffolding result
    vertices_of_regions_path : Path
        Path of the future file containing the regions' vertices
    """
    # TOTEST unit test write_vertices_of_regions
    with open(vertices_of_regions_path, 'w', encoding='utf-8') as f_out:
        for region_index in range(result.number_regions()):
            line: str = ''
            for v_ind, v_or, v_occ in result.region_occorc(region_index):
                line += f'{v_ind}\t{ORIENT_INT_STR[v_or]}\t{v_occ}\t'
            f_out.write(line[:-1] + '\n')


def read_vertices_of_regions(vertices_of_regions_path: Path) -> (
        Iterator[tuple[OccOrCT, ...]]):
    """Read the regions' vertices file.

    Parameters
    ----------
    vertices_of_regions_path : Path
        Path of the file containing the regions' vertices

    Yields
    ------
    tuple of OccOrCT
        List of vertices of one region
    """
    with open(vertices_of_regions_path, 'r', encoding='utf-8') as f_in:
        for line in f_in:
            vertices_of_region: list[OccOrCT] = []
            l_occorcstr = line.split('\t')
            k = 0
            while k < len(l_occorcstr) - 2:
                vertices_of_region.append(
                    (
                        IndexT(l_occorcstr[k]),
                        STR_ORIENT[l_occorcstr[k + 1]],  # type: ignore
                        IndexT(l_occorcstr[k + 2]),
                    ),
                )
                k += 3
            yield tuple(vertices_of_region)


def fmt_vertices_of_regions_filename(
        instance_name: str,
        ilp_combination: Iterable[RegionIDT]) -> str:
    """Format the vertices of regions file name.

    Parameters
    ----------
    instance_name : str
        Instance name
    ilp_combination : iterable of RegionIDT
        ILP string code combination

    Returns
    -------
    str
        Formatted file name
    """
    # TOTEST unit test fmt_vertices_of_regions_filename
    return (
        f'{VERTICES_OF_REGIONS_PREFIX}_{instance_name}'
        f"_{'_'.join(ilp_combination)}"
        f'.{VERTICES_OF_REGIONS_EXT}'
    )


# ---------------------------------------------------------------------------- #
#                           Found Repeated Fragments                           #
# ---------------------------------------------------------------------------- #
def write_found_repeated_fragments(var: Union[PuLPVarInvF, PuLPVarDirF],
                                   repeated_fragments_path: Path):
    r"""Write the repeated fragments found when solving a problem.

    DOCU file format
    * Format:
        ```md
        <code>\t<canonical>\n
        ```
    * Example:
        ```
        invf    1   +   2

        ```

    Parameters
    ----------
    var : PuLPVarInvF | PuLPVarDirF
        PuLP variable
    repeated_fragments_path : Path
        Path of the future file containing the repeated fragments solution
    """
    # TOTEST unit test write_found_repeated_fragments
    with open(repeated_fragments_path, 'w', encoding='utf-8') as f_out:
        if isinstance(var, PuLPVarInvF):
            for (v_ind, v_or, v_occ), _ in var.invf_solution():
                f_out.write(
                    f'{INVF_CODE}'
                    f'\t{v_ind}\t{ORIENT_INT_STR[v_or]}\t{v_occ}\n',
                )
        else:
            for (v_ind, v_or, v_occ), _ in var.dirf_solution():
                f_out.write(
                    f'{DIRF_CODE}'
                    f'\t{v_ind}\t{ORIENT_INT_STR[v_or]}\t{v_occ}\n',
                )


def read_found_repeated_fragments(
        repeated_fragments_path: Path) -> Iterator[tuple[str, OccOrCT]]:
    """Iterate over repeated fragments code and canonical.

    Parameters
    ----------
    repeated_fragments_path : Path
        Path of the file containing the repeated fragments solution

    Yields
    ------
    str
        Repeated fragments code
    OccOrCT
        Repeat fragments canonical
    """
    # TOTEST unit test read_found_repeated_fragments
    with open(repeated_fragments_path, 'r', encoding='utf-8') as f_in:
        for line in f_in:
            code_canonical = line.split()
            yield code_canonical[0], (
                IndexT(code_canonical[1]),
                STR_ORIENT[code_canonical[2]],  # type: ignore
                IndexT(code_canonical[3]),
            )


def fmt_found_repeated_fragments_filename(
        instance_name: str,
        ilp_combination: Iterable[RegionIDT]) -> str:
    """Format the found repeated fragments file name.

    Parameters
    ----------
    instance_name : str
        Instance name
    ilp_combination : iterable of RegionIDT
        ILP string code combination

    Returns
    -------
    str
        Formatted file name
    """
    # TOTEST unit test fmt_found_repeated_fragments_filename
    return (
        f'{FOUND_REPFRAG_PREFIX}_{instance_name}'
        f"_{'_'.join(ilp_combination)}"
        f'.{FOUND_REPFRAG_EXT}'
    )
