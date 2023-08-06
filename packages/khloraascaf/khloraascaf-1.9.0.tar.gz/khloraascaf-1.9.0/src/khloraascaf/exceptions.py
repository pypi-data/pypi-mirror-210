# -*- coding=utf-8 -*-

"""Scaffolding exceptions module."""

from collections.abc import Iterable
from pathlib import Path

from khloraascaf.lib import RegionIDT


# ============================================================================ #
#                                    CLASSES                                   #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                               Scaffolding Error                              #
# ---------------------------------------------------------------------------- #
class ScaffoldingError(Exception):
    """Scaffolding error exception."""

    def __init__(self, outdir: Path):
        """The Initialiser."""
        super().__init__()
        self.__outdir: Path = outdir

    def outdir_gen(self) -> Path:
        """Unique identifier output directory path.

        Returns
        -------
        Path
            Unique identifier output directory path
        """
        return self.__outdir

    def __str__(self) -> str:
        """Exception message."""
        return (
            'Scaffolding fails\n'
            f'\tSee output directory: {self.__outdir}'
        )


class RepeatScaffoldingError(Exception):
    """If the repeat scaffolding solving fails during the combination."""

    def __str__(self) -> str:
        """Exception message."""
        return 'Repeat scaffolding has failed'


class SingleCopyScaffoldingError(Exception):
    """If the single copy scaffolding solving fails during the combination."""

    def __str__(self) -> str:
        """Exception message."""
        return 'Single copy scaffolding has failed'


class CombineScaffoldingError(Exception):
    """Scaffolding combination error exception."""

    def __str__(self) -> str:
        """Print the exception message.

        Returns
        -------
        str
            Exception message
        """
        return 'The scaffolding combination has failed'


# ---------------------------------------------------------------------------- #
#                                 Region Types                                 #
# ---------------------------------------------------------------------------- #
class WrongRegionID(Exception):
    """Wrong region identifier exception."""

    def __init__(self, region_id: str):
        """The Initializer."""
        super().__init__()
        self.__region_id = region_id

    def region_id(self) -> str:
        """Wrong region identifier.

        Returns
        -------
        str
            Wrong region identifier
        """
        return self.__region_id

    def __str__(self) -> str:
        """Print the exception message.

        Returns
        -------
        str
            Exception message
        """
        return f"The region identifier '{self.__region_id}' is not correct"


# ---------------------------------------------------------------------------- #
#                                    Solver                                    #
# ---------------------------------------------------------------------------- #
class WrongSolverName(Exception):
    """Wrong solver name exception."""

    def __init__(self, solver: str):
        """The Initializer."""
        super().__init__()
        self.__solver = solver

    def solver(self) -> str:
        """Wrong solver name.

        Returns
        -------
        str
            Wrong solver name
        """
        return self.__solver

    def __str__(self) -> str:
        """Print the exception message.

        Returns
        -------
        str
            Exception message
        """
        return f'The solver name {self.__solver} is not correct'


# ---------------------------------------------------------------------------- #
#                                Unfeasible ILP                                #
# ---------------------------------------------------------------------------- #
class _UnfeasibleILP(Exception):
    """ILP problem unfeasible exception."""

    _PROBLEM_ID = 'THE PROBLEM'

    def __init__(self, status: str, ilp_combi: Iterable[RegionIDT]):
        super().__init__()
        self.__status: str = status
        self.__ilp_combi: tuple[RegionIDT, ...] = tuple(ilp_combi)

    def status(self) -> str:
        """Status.

        Returns
        -------
        str
            Status
        """
        return self.__status

    def ilp_combi(self) -> tuple[RegionIDT, ...]:
        """ILP code combination.

        Returns
        -------
        tuple of RegionIDT
            ILP code combination
        """
        return self.__ilp_combi

    def __str__(self) -> str:
        """Print the exception message.

        Returns
        -------
        str
            Exception message
        """
        return (
            f'The {self._PROBLEM_ID} problem is unfeasible:\n'
            '\t* ILP codes: '
            + '-'.join(self.__ilp_combi)
            + '\n'
            f'\t* Status: {self.__status}'
        )


class UnfeasibleIR(_UnfeasibleILP):
    """IR optimisation problem unfeasible exception."""

    _PROBLEM_ID = 'Find the best inverted repeats'


class UnfeasibleDR(_UnfeasibleILP):
    """DR optimisation problem unfeasible exception."""

    _PROBLEM_ID = 'Find the best direct repeats'


class UnfeasibleSC(_UnfeasibleILP):
    """SC optimisation problem unfeasible exception."""

    _PROBLEM_ID = 'Find the best single copy regions'


# ---------------------------------------------------------------------------- #
#                                 Result Error                                 #
# ---------------------------------------------------------------------------- #
class NotACircuit(Exception):
    """Not a circuit exception."""

    def __str__(self) -> str:
        """Print the exception message.

        Returns
        -------
        str
            Exception message
        """
        return 'The found path is not a circuit'


# ---------------------------------------------------------------------------- #
#                            Run Metadata Exception                            #
# ---------------------------------------------------------------------------- #
# TOTEST run metadata exc.
class NoSolution(Exception):
    """No solution exception."""

    def __str__(self) -> str:
        """Print the exception message.

        Returns
        -------
        str
            Exception message
        """
        return 'There is no solution'
