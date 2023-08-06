# -*- coding=utf-8 -*-

"""Heaviest presence score path PuLP ILP."""

from typing import Optional

from pulp import LpMaximize, LpProblem, lpSum

from khloraascaf.ilp.pulp_circuit import (
    circuit_from_the_starter_forward,
    flow_definition,
    intermediate_in_circuit,
)
from khloraascaf.ilp.pulp_repeated_fragments import (
    fix_repeats_subpaths,
    occurrences_priority,
)
from khloraascaf.ilp.pulp_var_db import PuLPVarPresScoreModel
from khloraascaf.multiplied_doubled_contig_graph import (
    CIND_IND,
    PRESSCORE_ATTR,
    MDCGraph,
    OccOrCT,
)
from khloraascaf.result import ScaffoldingResult


# ============================================================================ #
#                                  PULP MODEL                                  #
# ============================================================================ #
def best_presscore_model(mdcg: MDCGraph, starter_vertex: OccOrCT,
                         fix_result: Optional[ScaffoldingResult] = None) -> (
        tuple[LpProblem, PuLPVarPresScoreModel]):
    """Best path with highest presence score PuLP model.

    Parameters
    ----------
    mdcg : MDCGraph
        Multiplied doubled contig graph
    starter_vertex : OccOrCT
        Starter vertex
    fix_result : ScaffoldingResult, optional
        Previous scaffolding result, by default `None`

    Returns
    -------
    LpProblem
        ILP problem
    PuLPVarPresScoreModel
        ILP variables
    """
    # ------------------------------------------------------------------------ #
    # Constants
    # ------------------------------------------------------------------------ #
    big_m = mdcg.multiplied_card() // 2

    # ------------------------------------------------------------------------ #
    # Problem
    # ------------------------------------------------------------------------ #
    prob = LpProblem(name='best_presscore', sense=LpMaximize)

    # ------------------------------------------------------------------------ #
    # Variables
    # ------------------------------------------------------------------------ #
    var = PuLPVarPresScoreModel(mdcg, starter_vertex)

    # ------------------------------------------------------------------------ #
    # Objective function
    # ------------------------------------------------------------------------ #
    __presscore_objective(prob, var, mdcg)

    # ------------------------------------------------------------------------ #
    # Constraints
    # ------------------------------------------------------------------------ #
    #
    # Path constraints
    #
    flow_definition(prob, var, big_m, mdcg)
    circuit_from_the_starter_forward(prob, var, mdcg, starter_vertex)
    intermediate_in_circuit(prob, var, mdcg, starter_vertex)
    #
    # Fix repeats sub-paths
    #
    if fix_result is not None:
        fix_repeats_subpaths(prob, var, fix_result)
    #
    # Speed-up
    #
    occurrences_priority(prob, var, mdcg)
    return prob, var


# ============================================================================ #
#                              OBJECTIVE FUNCTION                              #
# ============================================================================ #
def __presscore_objective(prob: LpProblem, var: PuLPVarPresScoreModel,
                          mdcg: MDCGraph):
    """Invf model objective function.

    Parameters
    ----------
    prob : LpProblem
        PuLP problem
    var : PuLPVarPresScoreModel
        Variable data object
    mdcg : MDCGraph
        Multiplied doubled contig graph
    """
    vertices = mdcg.vertices()
    prob += lpSum(
        vertices.attr(v[CIND_IND], PRESSCORE_ATTR) * var.i[v]
        for v in var.i
    )
