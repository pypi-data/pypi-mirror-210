# -*- coding=utf-8 -*-

"""PuLP circuit model."""


from pulp import LpProblem, lpSum
from revsymg.index_lib import FORWARD_INT, REVERSE_INT

from khloraascaf.ilp.pulp_var_db import PuLPVarPath
from khloraascaf.multiplied_doubled_contig_graph import (
    CIND_IND,
    MULT_ATTR,
    MDCGraph,
    OccOrCT,
    rev_occorc,
)


# ============================================================================ #
#                                  CONSTRAINTS                                 #
# ============================================================================ #
def flow_definition(prob: LpProblem, var: PuLPVarPath,
                    big_m: int, mdcg: MDCGraph):
    """Constraint defining the flow on the edges.

    Parameters
    ----------
    prob : LpProblem
        PuLP problem
    var : PuLPVarPath
        Variables
    big_m : int
        Big M
    mdcg : MDCGraph
        Mulitplied doubled contig graph
    """
    for e in mdcg.multiplied_edges():
        #
        # If edge is chosen, then its flow is positive
        #
        prob += var.x[e] <= var.f[e]
        #
        # If edge is not chosen, then its flow is 0-negative
        #
        prob += var.f[e] <= big_m * var.x[e]


def circuit_from_the_starter_forward(prob: LpProblem, var: PuLPVarPath,
                                     mdcg: MDCGraph, starter_vertex: OccOrCT):
    """Constraint defining the path from start to terminal.

    Parameters
    ----------
    prob : LpProblem
        PuLP problem
    var : PuLPVarPath
        Variables
    mdcg : MDCGraph
        Multiplied doubled contig graph
    starter_vertex : OccOrCT
        Starter vertex
    """
    # ------------------------------------------------------------------------ #
    # Use the starter in forward orientation as the beginning of the circuit
    # ------------------------------------------------------------------------ #
    #
    # The path begins from the starter
    #
    prob += (
        lpSum(
            var.x[starter_vertex, v]
            for v in mdcg.multiplied_succs(starter_vertex)
        ) == 1
    )
    #
    # The path ends to the starter
    #
    prob += (
        lpSum(
            var.x[u, starter_vertex]
            for u in mdcg.multiplied_preds(starter_vertex)
        ) == 1
    )
    #
    # Flow is initialised to one
    #
    prob += (
        lpSum(
            var.f[starter_vertex, v]
            for v in mdcg.multiplied_succs(starter_vertex)
        ) == 1
    )
    # ------------------------------------------------------------------------ #
    # Avoid use of start reverse
    # ------------------------------------------------------------------------ #
    start_r = rev_occorc(starter_vertex)

    for u in mdcg.multiplied_preds(start_r):
        prob += var.x[u, start_r] == 0  # pylint: disable=compare-to-zero
    for v in mdcg.multiplied_succs(start_r):
        prob += var.x[start_r, v] == 0  # pylint: disable=compare-to-zero
    #
    # Flow is initialised to zero
    #
    prob += (
        lpSum(  # pylint: disable=compare-to-zero
            var.f[start_r, v]
            for v in mdcg.multiplied_succs(start_r)
        ) == 0
    )


def intermediate_in_circuit(prob: LpProblem, var: PuLPVarPath,
                            mdcg: MDCGraph, starter_vertex: OccOrCT):
    """Constraint defining the intermediate vertices in the circuit.

    Parameters
    ----------
    prob : LpProblem
        PuLP problem
    var : PuLPVarPath
        Variables
    mdcg : MDCGraph
        Multiplied doubled contig graph
    starter_vertex : OccOrCT
        Starter vertex
    """
    vertices = mdcg.vertices()

    # Intermediate are non-starter vertex (nor its reverse)
    for v_ind in (i for i in range(vertices.card_index())
                  if i != starter_vertex[CIND_IND]):

        for v_occ in range(vertices.attr(v_ind, MULT_ATTR)):

            v_f: OccOrCT = (v_ind, FORWARD_INT, v_occ)
            v_r: OccOrCT = (v_ind, REVERSE_INT, v_occ)
            #
            # Forward or reverse or nothing
            #
            prob += var.i[v_f] + var.i[v_r] <= 1

            for v in (v_f, v_r):
                #
                # Intermediate iif there is exactly one in-edge
                #   and one out-edge
                #
                prob += (
                    var.i[v]
                    == lpSum(var.x[u, v] for u in mdcg.multiplied_preds(v))
                )
                prob += (
                    var.i[v]
                    == lpSum(var.x[v, w] for w in mdcg.multiplied_succs(v))
                )
                #
                # Passing throw an intermediate increments its out-flow
                #
                prob += (
                    lpSum(var.f[v, w] for w in mdcg.multiplied_succs(v))
                    - lpSum(var.f[u, v] for u in mdcg.multiplied_preds(v))
                    == var.i[v]
                )
