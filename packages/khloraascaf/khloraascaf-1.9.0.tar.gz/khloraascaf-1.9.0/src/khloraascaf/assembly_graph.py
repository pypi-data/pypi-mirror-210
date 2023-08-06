# -*- coding=utf-8 -*-

"""Module for assembly graph and multiple solution generator."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path
from queue import LifoQueue

from bitarray import bitarray
from revsymg.graphs import RevSymGraph
from revsymg.index_lib import (
    FORWARD_INT,
    IND,
    ORIENT_REV,
    IndexT,
    IndOrIndT,
    IndOrT,
    OrT,
)

from khloraascaf.inputs import STR_ORIENT
from khloraascaf.lib import RegionIDT
from khloraascaf.outputs import (
    ORC_ID_IND,
    ORC_OR_IND,
    ORIENT_INT_STR,
    OrCT,
    read_contigs_of_regions,
    read_map_of_regions,
)
from khloraascaf.run_metadata import MetadataSolution


# DOCU: all assembly graph
# DOCU: tuto for assembly graph
# ============================================================================ #
#                                   CONSTANTS                                  #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                                     Files                                    #
# ---------------------------------------------------------------------------- #
#
# Region paths
#
REGION_PATHS_PREFIX = 'region_paths'
"""Prefix of the region paths file name."""
REGION_PATHS_EXT = 'tsv'
"""Extension of the region paths file"""
#
# Oriented contig paths
#
ORIENTED_CONTIG_PATHS_PREFIX = 'oriented_contig_paths'
"""Prefix of the oriented contig paths file name."""
ORIENTED_CONTIG_PATHS_EXT = 'tsv'
"""Extension of the oriented contig paths file"""


# ============================================================================ #
#                                     CLASS                                    #
# ============================================================================ #
class AssemblyGraph():
    """Khloraascaf assembly graph."""

    @classmethod
    def from_solution_metadata(
            cls, solution_metadata: MetadataSolution) -> AssemblyGraph:
        """Instantiate an AssemblyGraph object from a solution metadata.

        Parameters
        ----------
        solution_metadata : MetadataSolution
            Solution metadata

        Returns
        -------
        AssemblyGraph
            Assembly graph associated to the solution
        """
        outdir = solution_metadata.solution_directory()
        return cls(
            outdir / solution_metadata.map_of_regions(),
            outdir / solution_metadata.contigs_of_regions(),
        )

    def __init__(self, map_of_regions_path: Path,
                 contigs_of_regions_path: Path):
        """The Initializer."""
        self.__graph: RevSymGraph = RevSymGraph()
        self.__regions_contigs: list[tuple[OrCT, ...]] = []
        self.__region_path_length: int = 0
        self.__read_regions_contigs(contigs_of_regions_path)
        self.__add_regions_links(map_of_regions_path)

    def all_region_paths(self) -> Iterator[tuple[IndOrT, ...]]:  # noqa
        """Iterate over all the paths of oriented regions.

        Yields
        ------
        tuple of IndOrT
            Path of oriented regions
        """
        edges = self.__graph.edges()

        used_edges: bitarray = bitarray('0') * (
            edges.biggest_edge_index() + 1)

        starter = (0, FORWARD_INT)

        path: list[IndOrT] = [starter]
        eind_path: list[IndexT] = []
        #
        # The lifo contains the number of elements to keep to continue
        #   at the next remaning branch (first IndexT value)
        #
        lifo: LifoQueue[tuple[IndexT, IndOrT, IndexT]] = LifoQueue()

        for v, e_ind in edges.succs(starter):
            if v[IND] == starter[IND]:
                yield tuple(path)
            else:
                lifo.put((1, v, e_ind))

        while not lifo.empty():
            _, v, e_ind = lifo.get()
            path.append(v)
            eind_path.append(e_ind)
            used_edges[e_ind] = True

            vw_not_used: list[IndOrIndT] = []
            for w, f_ind in edges.succs(v):
                if w[IND] != starter[IND] and not used_edges[f_ind]:
                    vw_not_used.append((w, f_ind))

            if vw_not_used:
                for w, f_ind in vw_not_used:
                    lifo.put((len(path), w, f_ind))
            else:
                if len(path) == self.__region_path_length:
                    yield tuple(path)
                #
                # Back to the next branching vertex
                #
                if not lifo.empty():
                    branch_src_succ_eind = lifo.get()
                    lifo.put(branch_src_succ_eind)
                    for _ in range(len(path) - branch_src_succ_eind[0]):
                        path.pop()
                        used_edges[eind_path.pop()] = False

    def all_oriented_contig_paths(self) -> Iterator[tuple[OrCT, ...]]:
        """Iterate over all the paths of oriented contigs.

        Yields
        ------
        tuple of IndOrT
            Path of oriented contigs
        """
        # TODO don't use self method, to avoid verify path validity
        # (because it is known valid)
        for region_path in self.all_region_paths():
            yield tuple(self.region_path_to_oriented_contigs(region_path))

    def region_path_to_oriented_contigs(
            self, region_path: Iterable[IndOrT]) -> Iterator[OrCT]:
        """Iterate over the oriented contigs of a given region path.

        Parameters
        ----------
        region_path : iterable of IndOrT
            Path of oriented regions

        Yields
        ------
        OrCT
            Oriented contig
        """
        # TODO raise error if not a valid path
        for reg_ind, reg_or in region_path:
            yield from self.oriented_contigs_of_region(reg_ind, reg_or)

    # ~*~ Getter ~*~

    def revsymg(self) -> RevSymGraph:
        """Return the reverse symmetric graph associated.

        Returns
        -------
        RevSymGraph
            Reverse symmetric graph
        """
        return self.__graph

    def oriented_contigs_of_region(self, region_ind: IndexT,
                                   orientation: OrT = FORWARD_INT) -> (
            Iterator[OrCT]):
        """Iterate over oriented contigs of the oriented region.

        Parameters
        ----------
        region_ind : IndexT
            Region's index
        orientation : OrT, optional
            Region's orientation, by default FORWARD_INT

        Yields
        ------
        OrCT
            Oriented contig of the oriented region
        """
        if orientation == FORWARD_INT:
            yield from self.__regions_contigs[region_ind]
        else:
            for oriented_contig in reversed(self.__regions_contigs[region_ind]):
                yield rev_oriented_contig(oriented_contig)

    def region_path_length(self) -> int:
        """Return the length of all the region paths.

        Returns
        -------
        int
            _description_
        """
        return self.__region_path_length

    # ~*~ Private ~*~

    def __read_regions_contigs(self, contigs_of_regions_path: Path):
        """Extract the oriented contigs for each region.

        Parameters
        ----------
        contigs_of_regions_path : Path
            List of oriented contigs for each region
        """
        vertices = self.__graph.vertices()
        for region_ind, oriented_contigs in enumerate(
                read_contigs_of_regions(contigs_of_regions_path)):
            assert region_ind == vertices.add()
            self.__regions_contigs.append(oriented_contigs)

    def __add_regions_links(self, map_of_regions_path: Path):
        """Add regions links from map of regions.

        Parameters
        ----------
        map_of_regions_path : Path
            Map of regions
        """
        edges = self.__graph.edges()
        reg_indor_iter = read_map_of_regions(map_of_regions_path)
        start_indor = next(reg_indor_iter)
        u_indor = start_indor
        for v_indor in reg_indor_iter:
            edges.add(u_indor, v_indor)
            u_indor = v_indor
        edges.add(u_indor, start_indor)
        self.__region_path_length = len(self.__graph.edges()) // 2


# ============================================================================ #
#                                   FUNCTIONS                                  #
# ============================================================================ #
def rev_oriented_contig(oriented_contig: OrCT) -> OrCT:
    """Return the reverse of the oriented contig.

    Parameters
    ----------
    oriented_contig : OrCT
        Oriented contig

    Returns
    -------
    OrCT
        Its reverse
    """
    return oriented_contig[ORC_ID_IND], ORIENT_REV[oriented_contig[ORC_OR_IND]]


# ---------------------------------------------------------------------------- #
#                               Region Paths File                              #
# ---------------------------------------------------------------------------- #
def write_region_paths(region_paths: Iterable[Iterable[IndOrT]],
                       region_paths_file: Path):
    """Write the region paths file.

    Parameters
    ----------
    region_paths : iterable of iterable of IndOrT
        Region paths
    region_paths_file : Path
        Region paths file path
    """
    with open(region_paths_file, 'w', encoding='utf-8') as f_out:
        for region_path in region_paths:
            line: str = ''
            for reg_ind, reg_or in region_path:
                line += f'{reg_ind}\t{ORIENT_INT_STR[reg_or]}\t'
            f_out.write(line[:-1] + '\n')


def read_region_paths(region_paths_file: Path) -> Iterator[tuple[IndOrT, ...]]:
    """Read region paths from file.

    Parameters
    ----------
    region_paths_file : Path
        Region paths file path

    Yields
    ------
    tuple of IndOrT
        Region path
    """
    with open(region_paths_file, 'r', encoding='utf-8') as regpaths_in:
        for line in regpaths_in:
            region_path = []
            l_regindor = line.split()
            k = 0
            while k < len(l_regindor) - 1:
                region_path.append(
                    (
                        IndexT(l_regindor[k]),
                        STR_ORIENT[l_regindor[k + 1]],  # type: ignore
                    ),
                )
                k += 2
            yield tuple(region_path)


def fmt_region_paths_filename(instance_name: str,
                              ilp_combination: Iterable[RegionIDT]) -> str:
    """Format the region paths filename.

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
        f'{REGION_PATHS_PREFIX}_{instance_name}'
        f"_{'_'.join(ilp_combination)}"
        f'.{REGION_PATHS_EXT}'
    )


# ---------------------------------------------------------------------------- #
#                          Oriented Contig Paths File                          #
# ---------------------------------------------------------------------------- #
def write_oriented_contig_paths(oriented_contig_paths: Iterable[Iterable[OrCT]],
                                oriented_contig_paths_file: Path):
    """Write the oriented contig paths file.

    Parameters
    ----------
    oriented_contig_paths : iterable of iterable of OrCT
        Region paths
    oriented_contig_paths_file : Path
        Region paths file path
    """
    with open(oriented_contig_paths_file, 'w', encoding='utf-8') as f_out:
        for oriented_contig_path in oriented_contig_paths:
            line: str = ''
            for c_id, c_or in oriented_contig_path:
                line += f'{c_id}\t{ORIENT_INT_STR[c_or]}\t'
            f_out.write(line[:-1] + '\n')


def read_oriented_contig_paths(oriented_contig_paths_file: Path) -> (
        Iterator[tuple[OrCT, ...]]):
    """Read region paths from file.

    Parameters
    ----------
    oriented_contig_paths_file : Path
        Region paths file path

    Yields
    ------
    tuple of OrCT
        Oriented contig path
    """
    with open(oriented_contig_paths_file, 'r', encoding='utf-8') as regpaths_in:
        for line in regpaths_in:
            oriented_contig_path = []
            l_orc = line.split()
            k = 0
            while k < len(l_orc) - 1:
                oriented_contig_path.append(
                    (
                        l_orc[k],
                        STR_ORIENT[l_orc[k + 1]],  # type: ignore
                    ),
                )
                k += 2
            yield tuple(oriented_contig_path)


def fmt_oriented_contig_paths_filename(
        instance_name: str,
        ilp_combination: Iterable[RegionIDT]) -> str:
    """Format the oriented contig paths filename.

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
        f'{ORIENTED_CONTIG_PATHS_PREFIX}_{instance_name}'
        f"_{'_'.join(ilp_combination)}"
        f'.{ORIENTED_CONTIG_PATHS_EXT}'
    )
