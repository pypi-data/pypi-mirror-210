# -*- coding=utf-8 -*-

"""Module for the RunMetadata class."""


from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any, Optional

import yaml  # type: ignore
from pulp import LpStatus, LpStatusOptimal
from revsymg.index_lib import IndexT

from khloraascaf.cli import (
    ARG_CONTIG_ATTRS,
    ARG_CONTIG_LINKS,
    ARG_CONTIG_STARTER,
    OPT_INSTANCE_NAME,
    OPT_MULT_UPB,
    OPT_OUTDEBUG,
    OPT_OUTDIR,
    OPT_PRESSCORE_UPB,
    OPT_SOLVER,
)
from khloraascaf.exceptions import NoSolution
from khloraascaf.inputs import STR_ORIENT, IdCT, MultT, PresScoreT
from khloraascaf.lib import DR_REGION_ID, IR_REGION_ID, RegionIDT
from khloraascaf.multiplied_doubled_contig_graph import (
    CIND_IND,
    COCC_IND,
    COR_IND,
    OccOrCT,
)
from khloraascaf.outputs import (
    CONTIGS_OF_REGIONS_PREFIX,
    MAP_OF_REGIONS_PREFIX,
    ORIENT_INT_STR,
)
from khloraascaf.utils_debug import (
    FOUND_REPFRAG_PREFIX,
    VERTICES_OF_REGIONS_PREFIX,
)


# DOCU tuto metadata
# TOTEST metadata
# ============================================================================ #
#                                     CLASS                                    #
# ============================================================================ #
# DOCU IOConfig
# pylint: disable=too-many-instance-attributes
class IOConfig():
    """Input/Output config metadata class."""

    YAML_FILE: str = 'io_config.yaml'
    """IO config metadata file name."""

    @classmethod
    def from_run_directory(cls, ioconfig_dir: Path) -> IOConfig:
        """Intitialise IOConfig from the directory of the YAML.

        Parameters
        ----------
        ioconfig_dir : Path
            IO config metadata YAML directory

        Returns
        -------
        IOConfig
            IO config metadata
        """
        with open(ioconfig_dir / cls.YAML_FILE,
                  'r', encoding='utf-8') as f_in:
            io_dict: dict[str, Any] = yaml.load(f_in, yaml.Loader)
        return cls(
            ioconfig_dir,
            Path(io_dict[ARG_CONTIG_ATTRS]),
            Path(io_dict[ARG_CONTIG_LINKS]),
            io_dict[ARG_CONTIG_STARTER],
            MultT(io_dict[OPT_MULT_UPB]),
            PresScoreT(io_dict[OPT_PRESSCORE_UPB]),
            io_dict[OPT_SOLVER],
            Path(io_dict[OPT_OUTDIR]),
            io_dict[OPT_INSTANCE_NAME],
            bool(io_dict[OPT_OUTDEBUG]),
        )

    # pylint: disable=too-many-arguments
    def __init__(self, ioconfig_dir: Path, contig_attrs: Path,
                 contig_links: Path, contig_starter: IdCT,
                 mult_upb: MultT, presscore_upb: PresScoreT,
                 solver: str, outdir: Path, instance_name: str,
                 debug: bool):
        """The Initialiser.

        Parameters
        ----------
        ioconfig_dir : Path
            YAML file output directory path
        contig_attrs : Path
            Contig attributes file path
        contig_links : Path
            Contig links file path
        contig_starter : IdCT
            Starter contig's identifier
        mult_upb : MultT
            Multiplicities upper bound
        presscore_upb : PresScoreT
            Presence score upper bound
        solver : str
            MILP solver to use
        outdir : Path
            Output directory path
        instance_name : str
            Instance name
        debug : bool
            Output debug or not
        """
        self.__ioconfig_dir: Path = ioconfig_dir
        self.__contig_attrs: Path = contig_attrs
        self.__contig_links: Path = contig_links
        self.__contig_starter: IdCT = contig_starter
        self.__mult_upb: MultT = mult_upb
        self.__presscore_upb: PresScoreT = presscore_upb
        self.__solver: str = solver
        self.__outdir: Path = outdir
        self.__instance_name: str = instance_name
        self.__debug: bool = debug

    # ~*~ Getter ~*~

    def io_config_directory(self) -> Path:
        """IO config directory path.

        Returns
        -------
        Path
            IO config directory path
        """
        return self.__ioconfig_dir

    def contig_attrs(self) -> Path:
        """Contig attributes file path.

        Returns
        -------
        Path
            Contig attributes file path
        """
        return self.__contig_attrs

    def contig_links(self) -> Path:
        """Contig links file path.

        Returns
        -------
        Path
            Contig links file path
        """
        return self.__contig_links

    def contig_starter(self) -> IdCT:
        """Contig starter identifier.

        Returns
        -------
        IdCT
            Contig starter identifier
        """
        return self.__contig_starter

    def mult_upb(self) -> MultT:
        """Multiplicity upper-bound.

        Returns
        -------
        MultT
            Multiplicity upper-bound
        """
        return self.__mult_upb

    def presscore_upb(self) -> PresScoreT:
        """Presence score upper-bound.

        Returns
        -------
        PresScoreT
            Presence score upper-bound
        """
        return self.__presscore_upb

    def solver(self) -> str:
        """MILP solver identifier.

        Returns
        -------
        str
            MILP solver identifier
        """
        return self.__solver

    def outdir(self) -> Path:
        """Output directory given by the user.

        Returns
        -------
        Path
            Output directory.
        """
        return self.__outdir

    def instance_name(self) -> str:
        """Instance name.

        Returns
        -------
        str
            Instance name
        """
        return self.__instance_name

    def debug(self) -> bool:
        """Debug option value.

        Returns
        -------
        bool
            Debug option value
        """
        return self.__debug

    # ~*~ I/O ~*~

    def write_yaml(self):
        """Write to a YAML file.

        Warning
        -------
        Write a file.
        """
        with open(self.yaml_path(), 'w', encoding='utf-8') as yaml_out:
            yaml_out.write(
                yaml.dump(
                    {
                        ARG_CONTIG_ATTRS: str(self.__contig_attrs),
                        ARG_CONTIG_LINKS: str(self.__contig_links),
                        ARG_CONTIG_STARTER: self.__contig_starter,
                        OPT_MULT_UPB: self.__mult_upb,
                        OPT_PRESSCORE_UPB: self.__presscore_upb,
                        OPT_SOLVER: self.__solver,
                        OPT_OUTDIR: str(self.__outdir),
                        OPT_INSTANCE_NAME: self.__instance_name,
                        OPT_OUTDEBUG: self.__debug,
                    },
                    sort_keys=False,
                ),
            )

    def yaml_path(self) -> Path:
        """YAML file path.

        Returns
        -------
        Path
            YAML file path
        """
        return self.__ioconfig_dir / self.YAML_FILE


# DOCU MetadataSolution
class MetadataSolution():
    """Solution metadata class."""

    YAML_FILE: str = 'solution.yaml'
    """Solution metadata file name."""

    KEY_ILP_COMBINATION = 'ilp_combination'

    @classmethod
    def there_is_a_solution(cls, dir_path: Path) -> bool:
        """Answer "is there a solution in the directory?".

        Parameters
        ----------
        dir_path : Path
            Directory path

        Returns
        -------
        bool
            True if there is a solution, else False
        """
        return (dir_path / cls.YAML_FILE).exists()

    @classmethod
    def from_run_directory(cls, yaml_dir: Path) -> MetadataSolution:
        """Intitialise MetadataSolution from the YAML's directory.

        Parameters
        ----------
        yaml_dir : Path
            Solution metadata YAML directory

        Returns
        -------
        MetadataSolution
            Solution metadata

        Raises
        ------
        NoSolution
            There is no solution
        """
        if not (yaml_dir / cls.YAML_FILE).exists():
            raise NoSolution()

        with open(yaml_dir / cls.YAML_FILE, 'r', encoding='utf-8') as f_in:
            sol_dict: dict[str, Any] = yaml.load(f_in, yaml.Loader)

        return cls(
            yaml_dir,
            sol_dict[cls.KEY_ILP_COMBINATION],
            Path(sol_dict[CONTIGS_OF_REGIONS_PREFIX]),
            Path(sol_dict[MAP_OF_REGIONS_PREFIX]),
        )

    # pylint: disable=too-many-arguments
    def __init__(self, solution_dir: Path,
                 ilp_combi: Iterable[RegionIDT],
                 contigs_of_regions_path: Path,
                 map_of_regions_path: Path):
        """The Initialiser.

        Parameters
        ----------
        solution_dir : Path
            Solution's path
        ilp_combi : iterable of RegionIDT
            Succession of region identifiers
        contigs_of_regions_path : Path
            Contigs of regions file path
        map_of_regions_path : Path
            Map of regions file path
        """
        self.__sol_dir: Path = solution_dir
        self.__ilp_combi: list[RegionIDT] = list(ilp_combi)
        self.__contigs_of_regions_path: Path = contigs_of_regions_path
        self.__map_of_regions_path: Path = map_of_regions_path

    # ~*~ Getter ~*~

    def solution_directory(self) -> Path:
        """Solution directory path.

        Returns
        -------
        Path
            Solution directory path
        """
        return self.__sol_dir

    def ilp_combination(self) -> list[RegionIDT]:
        """ILP succession.

        Returns
        -------
        list of RegionIDT
            ILP succession
        """
        return self.__ilp_combi

    def contigs_of_regions(self) -> Path:
        """Contigs of regions file path.

        Returns
        -------
        Path
            Contigs of regions file path
        """
        return self.__contigs_of_regions_path

    def map_of_regions(self) -> Path:
        """Map of regions file path.

        Returns
        -------
        Path
            Map of regions file path
        """
        return self.__map_of_regions_path

    # ~*~ I/O ~*~

    def write_yaml(self):
        """Write to a YAML file.

        Warning
        -------
        Write a file.
        """
        with open(self.yaml_path(), 'w', encoding='utf-8') as yaml_out:
            yaml_out.write(
                yaml.dump(
                    {
                        self.KEY_ILP_COMBINATION: self.__ilp_combi,
                        CONTIGS_OF_REGIONS_PREFIX:
                        str(self.__contigs_of_regions_path),
                        MAP_OF_REGIONS_PREFIX:
                        str(self.__map_of_regions_path),
                    },
                    sort_keys=False,
                ),
            )

    def yaml_path(self) -> Path:
        """YAML file path.

        Returns
        -------
        Path
            YAML file path
        """
        return self.__sol_dir / self.YAML_FILE


class MetadataAllSolutions():
    """Solutions metadata class."""

    YAML_FILE: str = 'solutions.yaml'
    """All solutions metadata file name."""

    KEY_ILP_COMBINATION = 'ilp_combination'

    @classmethod
    def there_is_a_solution(cls, dir_path: Path) -> bool:
        """Answer "is there a solution in the directory?".

        Parameters
        ----------
        dir_path : Path
            Directory path

        Returns
        -------
        bool
            True if there is a solution, else False
        """
        return (dir_path / cls.YAML_FILE).exists()

    @classmethod
    def from_run_directory(cls, yaml_dir: Path) -> MetadataAllSolutions:
        """Intitialise MetadataAllSolutions from the YAML's directory.

        Parameters
        ----------
        yaml_dir : Path
            Solution metadata YAML directory

        Returns
        -------
        MetadataAllSolutions
            Solutions metadata
        """
        if not (yaml_dir / cls.YAML_FILE).exists():
            return cls(yaml_dir, ())
        with open(yaml_dir / cls.YAML_FILE, 'r', encoding='utf-8') as f_in:
            sol_list: list[dict[str, Any]] = yaml.load(f_in, yaml.Loader)
        return cls(
            yaml_dir,
            (
                MetadataSolution(
                    yaml_dir, sol_dict[cls.KEY_ILP_COMBINATION],
                    Path(sol_dict[CONTIGS_OF_REGIONS_PREFIX]),
                    Path(sol_dict[MAP_OF_REGIONS_PREFIX]),
                )
                for sol_dict in sol_list
            ),
        )

    # pylint: disable=too-many-arguments
    def __init__(self, solutions_dir: Path,
                 solutions: Iterable[MetadataSolution]):
        """The Initialiser.

        Parameters
        ----------
        solutions_dir : Path
            Solutions' directory path
        solutions : iterable of MetadataSolution
            Set of solution metadata
        """
        self.__sol_dir: Path = solutions_dir
        self.__solutions = list(solutions)

    # ~*~ Getter ~*~

    def solutions_directory(self) -> Path:
        """Solutions directory path.

        Returns
        -------
        Path
            Solutions directory path
        """
        return self.__sol_dir

    # ~*~ I/O ~*~

    def write_yaml(self, append_yaml: bool = False):
        """Write the solutions metadata to a YAML file.

        Parameters
        ----------
        append_yaml : bool
            If append to potentially already existing YAML file,
            by default False

        Warning
        -------
        Write a file.
        """
        write_mode = 'a' if append_yaml else 'w'

        with open(self.yaml_path(), write_mode, encoding='utf-8') as yaml_out:
            yaml_out.write(
                yaml.dump(
                    [
                        {
                            self.KEY_ILP_COMBINATION:
                            solution.ilp_combination(),
                            CONTIGS_OF_REGIONS_PREFIX:
                            str(solution.contigs_of_regions()),
                            MAP_OF_REGIONS_PREFIX:
                            str(solution.map_of_regions()),
                        } for solution in self.__solutions
                    ],
                    sort_keys=False,
                ),
            )

    def yaml_path(self) -> Path:
        """YAML file path.

        Returns
        -------
        Path
            YAML file path
        """
        return self.__sol_dir / self.YAML_FILE

    # ~*~ Special ~*~

    def __iter__(self) -> Iterator[MetadataSolution]:
        """Iterate over the solution metadata.

        Yields
        ------
        MetadataSolution
            Solution metadata
        """
        yield from self.__solutions

    def __len__(self) -> int:
        """Return the number of solution metadata.

        Returns
        -------
        int
            Number of solution metadata
        """
        return len(self.__solutions)


# DOCU MetadataDebug
class MetadataDebug():
    """Debug metadata class."""

    YAML_FILE: str = 'debug.yaml'
    """Debug metadata file name."""

    KEY_ILP_COMBINATION = 'ilp_combination'
    KEY_STARTER_VERTEX = 'starter_vertex'
    KEY_OPT_VALUE = 'opt_value'
    KEY_ILP_STATUS = 'ilp_status'

    @classmethod
    def from_run_directory(cls, yaml_dir: Path) -> MetadataDebug:
        """Intitialise MetadataDebug from the YAML's directory.

        Parameters
        ----------
        yaml_dir : Path
            Debug metadata YAML directory

        Returns
        -------
        MetadataDebug
            Debug metadata
        """
        with open(yaml_dir / cls.YAML_FILE,
                  'r', encoding='utf-8') as f_in:
            debug_dict: dict[str, Any] = yaml.load(f_in, yaml.Loader)
        return cls(
            yaml_dir,
            debug_dict[cls.KEY_ILP_COMBINATION],
            str_to_vertex(debug_dict[cls.KEY_STARTER_VERTEX]),
            debug_dict[cls.KEY_ILP_STATUS],
            (
                float(debug_dict[cls.KEY_OPT_VALUE])
                if cls.KEY_OPT_VALUE in debug_dict else None
            ),
            (
                Path(debug_dict[VERTICES_OF_REGIONS_PREFIX])
                if VERTICES_OF_REGIONS_PREFIX in debug_dict else None
            ),
            (
                Path(debug_dict[MAP_OF_REGIONS_PREFIX])
                if MAP_OF_REGIONS_PREFIX in debug_dict else None
            ),
            (
                Path(debug_dict[FOUND_REPFRAG_PREFIX])
                if FOUND_REPFRAG_PREFIX in debug_dict else None
            ),
        )

    # pylint: disable=too-many-arguments
    def __init__(self, run_dir: Path,
                 ilp_combi: Iterable[RegionIDT],
                 starter_vertex: OccOrCT,
                 ilp_status: str,
                 opt_value: float | None = None,
                 vertices_of_regions_path: Path | None = None,
                 map_of_regions_path: Path | None = None,
                 repeat_fragments_path: Path | None = None):
        """The Initialiser.

        Parameters
        ----------
        run_dir : Path
            Run path
        ilp_combi : iterable of RegionIDT
            Succession of region identifiers
        starter_vertex : OccOrCT
            Starter vertex
        ilp_status : str
            ILP solver status
        opt_value : float | None
            Optimal ILP value, optional
        vertices_of_regions_path : Path | None
            Vertices of regions file path, optional
        map_of_regions_path : Path | None
            Map of regions file path, optional
        repeat_fragments_path : Path | None
            Repeated fragments path, optional
        """
        self.__run_dir: Path = run_dir
        self.__ilp_combi: list[RegionIDT] = list(ilp_combi)
        self.__starter_vertex: OccOrCT = starter_vertex
        self.__ilp_status: str = ilp_status
        self.__opt_value: float | None = opt_value
        self.__vertices_of_regions_path: Path | None = vertices_of_regions_path
        self.__map_of_regions_path: Path | None = map_of_regions_path
        self.__repeat_fragments_path: Path | None = repeat_fragments_path

    # ~*~ Getter ~*~

    def run_directory(self) -> Path:
        """Run directory path.

        Returns
        -------
        Path
            Run directory path
        """
        return self.__run_dir

    def ilp_combination(self) -> list[RegionIDT]:
        """ILP succession.

        Returns
        -------
        list of RegionIDT
            ILP succession
        """
        return self.__ilp_combi

    def starter_vertex(self) -> OccOrCT:
        """Starter vertex.

        Returns
        -------
        OccOrCT
            Starter vertex
        """
        return self.__starter_vertex

    def ilp_status(self) -> str:
        """ILP string status.

        Returns
        -------
        str
            ILP string status
        """
        return self.__ilp_status

    def opt_value(self) -> Optional[float]:
        """ILP optimal value if any.

        Returns
        -------
        float | None
            Optimal value, else None
        """
        return self.__opt_value

    def vertices_of_regions(self) -> Path:
        """Vertices of regions file path.

        Returns
        -------
        Path
            Vertices of regions file path

        Raises
        ------
        FileNotFoundError
            File does not exist
        """
        if self.__vertices_of_regions_path is None:
            raise FileNotFoundError()
        return self.__vertices_of_regions_path

    def map_of_regions(self) -> Path:
        """Map of regions file path.

        Returns
        -------
        Path
            Map of regions file path

        Raises
        ------
        FileNotFoundError
            File does not exist
        """
        if self.__map_of_regions_path is None:
            raise FileNotFoundError()
        return self.__map_of_regions_path

    def repeat_fragments(self) -> Path:
        """Repeated fragments file path.

        Returns
        -------
        Path
            Repeated fragments file path

        Raises
        ------
        FileNotFoundError
            File does not exist
        """
        if self.__repeat_fragments_path is None:
            raise FileNotFoundError()
        return self.__repeat_fragments_path

    # ~*~ I/O ~*~

    def write_yaml(self):
        """Write the debug metadata to a YAML file.

        Warning
        -------
        Write a file.
        """
        dict_debug: dict[str, Any] = {
            self.KEY_ILP_COMBINATION: self.__ilp_combi,
            self.KEY_STARTER_VERTEX:
            vertex_to_str(self.__starter_vertex),
            self.KEY_ILP_STATUS: self.__ilp_status,
        }
        if self.__ilp_status == LpStatus[LpStatusOptimal]:
            assert self.__opt_value is not None
            assert self.__vertices_of_regions_path is not None
            assert self.__map_of_regions_path is not None
            dict_debug.update(
                {
                    self.KEY_OPT_VALUE: self.__opt_value,
                    VERTICES_OF_REGIONS_PREFIX:
                    str(self.__vertices_of_regions_path),
                    MAP_OF_REGIONS_PREFIX:
                    str(self.__map_of_regions_path),
                },
            )
            if self.__ilp_combi[-1] in (IR_REGION_ID, DR_REGION_ID):
                assert self.__repeat_fragments_path is not None
                dict_debug.update(
                    {
                        FOUND_REPFRAG_PREFIX:
                        str(self.__repeat_fragments_path),
                    },
                )

        with open(self.yaml_path(), 'w', encoding='utf-8') as yaml_out:
            yaml_out.write(yaml.dump(dict_debug, sort_keys=False))

    def yaml_path(self) -> Path:
        """YAML file path.

        Returns
        -------
        Path
            YAML file path
        """
        return self.__run_dir / self.YAML_FILE


class MetadataAllDebugs():
    """Debugs metadata class."""

    YAML_FILE: str = 'debugs.yaml'
    """All debugs metadata file name."""

    KEY_ILP_COMBINATION = 'ilp_combination'
    KEY_STARTER_VERTEX = 'starter_vertex'
    KEY_OPT_VALUE = 'opt_value'
    KEY_ILP_STATUS = 'ilp_status'

    @classmethod
    def from_run_directory(cls, yaml_dir: Path) -> MetadataAllDebugs:
        """Intitialise MetadataAllDebugs from the YAML's directory.

        Parameters
        ----------
        yaml_dir : Path
            Debugs metadata YAML directory

        Returns
        -------
        MetadataAllDebugs
            Debugs metadata
        """
        with open(yaml_dir / cls.YAML_FILE,
                  'r', encoding='utf-8') as f_in:
            debug_list: list[dict[str, Any]] = yaml.load(f_in, yaml.Loader)
        return cls(
            yaml_dir,
            (
                MetadataDebug(
                    yaml_dir, debug_dict[cls.KEY_ILP_COMBINATION],
                    str_to_vertex(debug_dict[cls.KEY_STARTER_VERTEX]),
                    debug_dict[cls.KEY_ILP_STATUS],
                    (
                        float(debug_dict[cls.KEY_OPT_VALUE])
                        if cls.KEY_OPT_VALUE in debug_dict else None
                    ),
                    (
                        Path(debug_dict[VERTICES_OF_REGIONS_PREFIX])
                        if VERTICES_OF_REGIONS_PREFIX in debug_dict else None
                    ),
                    (
                        Path(debug_dict[MAP_OF_REGIONS_PREFIX])
                        if MAP_OF_REGIONS_PREFIX in debug_dict else None
                    ),
                    (
                        Path(debug_dict[FOUND_REPFRAG_PREFIX])
                        if FOUND_REPFRAG_PREFIX in debug_dict else None
                    ),
                )
                for debug_dict in debug_list
            ),
        )

    # pylint: disable=too-many-arguments
    def __init__(self, debugs_dir: Path,
                 debugs: Iterable[MetadataDebug]):
        """The Initialiser.

        Parameters
        ----------
        debugs_dir : Path
            Debugs' directory path
        debugs : iterable of MetadataDebug
            Set of debug metadata
        """
        self.__run_dir: Path = debugs_dir
        self.__debugs = list(debugs)

    # ~*~ Getter ~*~

    def runs_directory(self) -> Path:
        """Runs directory path.

        Returns
        -------
        Path
            Runs directory path
        """
        return self.__run_dir

    # ~*~ I/O ~*~

    def write_yaml(self, append_yaml: bool = False):
        """Write the debugs metadata to a YAML file.

        Parameters
        ----------
        append_yaml : bool
            If append to potentially already existing YAML file,
            by default False

        Warning
        -------
        Write a file.
        """
        debug_list: list = []
        for debug in self.__debugs:
            dict_debug: dict[str, Any] = {
                self.KEY_ILP_COMBINATION: debug.ilp_combination(),
                self.KEY_STARTER_VERTEX:
                vertex_to_str(debug.starter_vertex()),
                self.KEY_ILP_STATUS: debug.ilp_status(),
            }
            if debug.ilp_status() == LpStatus[LpStatusOptimal]:
                assert debug.opt_value() is not None
                assert debug.vertices_of_regions() is not None
                assert debug.map_of_regions() is not None
                dict_debug.update(
                    {
                        self.KEY_OPT_VALUE: debug.opt_value(),
                        VERTICES_OF_REGIONS_PREFIX:
                        str(debug.vertices_of_regions()),
                        MAP_OF_REGIONS_PREFIX:
                        str(debug.map_of_regions()),
                    },
                )
                if debug.ilp_combination()[-1] in (IR_REGION_ID, DR_REGION_ID):
                    assert debug.repeat_fragments() is not None
                    dict_debug.update(
                        {
                            FOUND_REPFRAG_PREFIX:
                            str(debug.repeat_fragments()),
                        },
                    )
            debug_list.append(dict_debug)

        write_mode = 'a' if append_yaml else 'w'
        with open(self.yaml_path(), write_mode, encoding='utf-8') as yaml_out:
            yaml_out.write(yaml.dump(debug_list, sort_keys=False))

    def yaml_path(self) -> Path:
        """YAML file path.

        Returns
        -------
        Path
            YAML file path
        """
        return self.__run_dir / self.YAML_FILE

    # ~*~ Special ~*~

    def __iter__(self) -> Iterator[MetadataDebug]:
        """Iterate over the debug metadata.

        Yields
        ------
        MetadataDebug
            Solution metadata
        """
        yield from self.__debugs

    def __len__(self) -> int:
        """Return the number of debug metadata.

        Returns
        -------
        int
            Number of debug metadata
        """
        return len(self.__debugs)


# ============================================================================ #
#                                   FUNCTIONS                                  #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                               String Formatter                               #
# ---------------------------------------------------------------------------- #
def vertex_to_str(vertex: OccOrCT) -> str:
    """Transform a vertex to a string.

    Parameters
    ----------
    vertex : OccOrCT
        Vertex

    Returns
    -------
    str
        String representation
    """
    return (
        f'{vertex[CIND_IND]}'
        f'\t{ORIENT_INT_STR[vertex[COR_IND]]}'
        f'\t{vertex[COCC_IND]}'
    )


def str_to_vertex(vertex_str: str) -> OccOrCT:
    """Transform a vertex string to the vertex.

    Parameters
    ----------
    vertex_str : str
        Vertex string

    Returns
    -------
    OccOrCT
        Vertex
    """
    str_list = vertex_str.split('\t')
    return (
        IndexT(str_list[CIND_IND]),
        STR_ORIENT[str_list[COR_IND]],  # type: ignore
        IndexT(str_list[COCC_IND]),
    )
