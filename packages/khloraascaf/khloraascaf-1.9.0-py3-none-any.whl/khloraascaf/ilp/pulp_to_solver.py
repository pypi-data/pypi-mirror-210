# -*- coding=utf-8 -*-

"""Solve integer linear programs module."""

from __future__ import annotations, division

from collections.abc import Iterable
from pathlib import Path
from typing import Optional

from pulp import GUROBI_CMD, PULP_CBC_CMD, LpProblem

from khloraascaf.exceptions import WrongSolverName
from khloraascaf.inputs import SOLVER_CBC, SOLVER_GUROBI
from khloraascaf.lib import RegionIDT


# ============================================================================ #
#                                   CONSTANTS                                  #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                                   Log File                                   #
# ---------------------------------------------------------------------------- #
SOLVER_LOG_PREFIX = 'solver'
"""Prefix of the solver log file name."""

LOG_EXT = 'log'
"""Extension of the solver log file."""


# ============================================================================ #
#                                   FUNCTIONS                                  #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                                 Solve Models                                 #
# ---------------------------------------------------------------------------- #
def solve_pulp_problem(prob: LpProblem, solver: str,
                       log_path: Optional[Path] = None):
    """Instanciate and solve the PuLP model.

    Parameters
    ----------
    prob : LpProblem
        PuLP problem
    solver : str
        MILP solver to use ('cbc' or 'gurobi')
    log_path : Path, optional
        Solver log file path, by default `None`

    Raises
    ------
    WrongSolverName
        The solver name is not correct
    """
    if solver == SOLVER_CBC:
        SolverCmd = PULP_CBC_CMD
    elif solver == SOLVER_GUROBI:
        SolverCmd = GUROBI_CMD
    else:
        raise WrongSolverName(solver)
    prob.solve(SolverCmd(msg=0, logPath=log_path))


# ---------------------------------------------------------------------------- #
#                                Logs Formatters                               #
# ---------------------------------------------------------------------------- #
def fmt_solver_log_name(solver: str,
                        instance_name: str,
                        ilp_combination: Iterable[RegionIDT]) -> str:
    """Format solver log file name.

    Parameters
    ----------
    solver : str
        Solver name
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
        f'{SOLVER_LOG_PREFIX}_{solver}_{instance_name}'
        f"_{'_'.join(ilp_combination)}"
        f'.{LOG_EXT}'
    )
