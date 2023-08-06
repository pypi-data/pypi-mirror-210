# -*- coding=utf-8 -*-

"""Intersected direct fragments PuLP ILP."""


from typing import Optional

from pulp import LpMaximize, LpProblem

from khloraascaf.ilp.pulp_circuit import (
    circuit_from_the_starter_forward,
    flow_definition,
    intermediate_in_circuit,
)
from khloraascaf.ilp.pulp_repeated_fragments import (
    adjacent_fragments,
    alpha_definition,
    fix_repeats_subpaths,
    forbidden_pairing_definition,
    longuest_contiguous_repeat,
    occurrences_priority,
    pairs_in_path,
    pairs_priority,
)
from khloraascaf.ilp.pulp_var_db import PuLPVarDirFModel
from khloraascaf.multiplied_doubled_contig_graph import MDCGraph, OccOrCT
from khloraascaf.result import ScaffoldingResult


# ============================================================================ #
#                                  PULP MODEL                                  #
# ============================================================================ #
def intersected_dirf_model(mdcg: MDCGraph, starter_vertex: OccOrCT,
                           fix_result: Optional[ScaffoldingResult] = None) -> (
        tuple[LpProblem, PuLPVarDirFModel]):
    """Intersected direct fragments PuLP model.

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
    PuLPVarDirFModel
        ILP variables
    """
    # ------------------------------------------------------------------------ #
    # Constants
    # ------------------------------------------------------------------------ #
    big_m = mdcg.multiplied_card() // 2

    # ------------------------------------------------------------------------ #
    # Problem
    # ------------------------------------------------------------------------ #
    prob = LpProblem(name='inters_dirf', sense=LpMaximize)

    # ------------------------------------------------------------------------ #
    # Variables
    # ------------------------------------------------------------------------ #
    var = PuLPVarDirFModel(mdcg, starter_vertex)

    # ------------------------------------------------------------------------ #
    # Objective function
    # ------------------------------------------------------------------------ #
    longuest_contiguous_repeat(prob, var, mdcg)

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
    # Repeats constraints
    #
    pairs_in_path(prob, var, mdcg)
    alpha_definition(prob, var, mdcg, big_m)
    forbidden_pairing_definition(prob, var, mdcg)
    adjacent_fragments(prob, var, mdcg)
    #
    # Fix repeats sub-paths
    #
    if fix_result is not None:
        fix_repeats_subpaths(prob, var, fix_result)
        # TODO avoid pairs for fixed sub-paths
    else:
        #
        # Speed-up
        #
        pairs_priority(prob, var, mdcg)
    #
    # Speed-up
    #
    occurrences_priority(prob, var, mdcg)

    return prob, var
