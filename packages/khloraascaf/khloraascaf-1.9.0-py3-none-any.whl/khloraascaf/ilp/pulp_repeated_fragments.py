# -*- coding=utf-8 -*-

"""PuLP path model."""


from pulp import LpAffineExpression, LpProblem, lpSum
from revsymg.index_lib import FORWARD_INT, REVERSE_INT

from khloraascaf.ilp.dirf_sets import dirf_other
from khloraascaf.ilp.invf_sets import invf_other
from khloraascaf.ilp.pulp_var_db import (
    PuLPVarModelT,
    PuLPVarPath,
    PuLPVarRepFModelT,
)
from khloraascaf.multiplied_doubled_contig_graph import (
    MULT_ATTR,
    MDCGraph,
    OccOrCT,
)
from khloraascaf.result import ScaffoldingResult


# ============================================================================ #
#                                  OBJECTIVES                                  #
# ============================================================================ #
def longuest_contiguous_repeat(prob: LpProblem,
                               var: PuLPVarRepFModelT,
                               mdcg: MDCGraph):
    """Pair of the longuest contigous repeats model objective function.

    Parameters
    ----------
    prob : LpProblem
        PuLP problem
    var : PuLPVarInvFModel or PuLPVarDirFModel
        PuLP variables
    mdcg : MDCGraph
        Multiplied doubled contig graph
    """
    prob += (
        lpSum(var.m[p] for p in type(var).repeat_frag_fn(mdcg))
        + lpSum(var.isadj[q] for q in type(var).adj_repeat_frag_fn(mdcg))
    )


# ============================================================================ #
#                                  CONSTRAINTS                                 #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                      Repeats Are Sub-paths In The Graph                      #
# ---------------------------------------------------------------------------- #
def pairs_in_path(prob: LpProblem,
                  var: PuLPVarRepFModelT,
                  mdcg: MDCGraph):
    """Constraint defining the link between m and i variables.

    Parameters
    ----------
    prob : LpProblem
        PuLP problem
    var : PuLPVarInvFModel or PuLPVarDirFModel
        PuLP variables
    mdcg : MDCGraph
        Multiplied doubled contig graph
    """
    for i, j in type(var).repeat_frag_fn(mdcg):
        #
        # If the repeated fragment is chosen,
        #   then the first part is in the path
        #
        prob += (
            var.m[i, j] <= var.i[i]
        )
        #
        # If the repeated fragment is chosen,
        #   then the second part is in the path
        #
        prob += (
            var.m[i, j] <= var.i[j]
        )


# ---------------------------------------------------------------------------- #
#                               Repeat Structure                               #
# ---------------------------------------------------------------------------- #
#
# Definitions of relative positioning of two vertices that involves
#   in the path and are candidate of repeats
#
def alpha_definition(prob: LpProblem,
                     var: PuLPVarRepFModelT,
                     mdcg: MDCGraph, big_m: int):
    r"""Constraint defining alpha variables.

    Parameters
    ----------
    prob : LpProblem
        PuLP problem
    var : PuLPVarInvFModel or PuLPVarDirFModel
        PuLP variables
    mdcg : MDCGraph
        Multiplied doubled contig graph
    big_m : int
        Big-M constant

    Notes
    -----
    It was observed (not rigorously) that forcing :math:`\alpha_{uv} = 0`
    when :math:`y_u = y_v` is faster than forcing :math:`\alpha_{uv} = 1`
    """
    for u, v in type(var).pair_repeat_alpha_fn(mdcg):
        #
        # If v is after u, then alpha_uv = 1
        #
        prob += pos(var, mdcg, v) - pos(var, mdcg, u) <= var.alpha(u, v) * big_m
        #
        # If u is after v, then alpha_uv = 0
        #
        prob += (
            pos(var, mdcg, u) - pos(var, mdcg, v)
            <= (1 - var.alpha(u, v)) * big_m
        )
        #
        # If u and v are not positioned (pos_u + pos_v = 0),
        #   then alpha_uv = 0
        #
        prob += pos(var, mdcg, u) + pos(var, mdcg, v) >= var.alpha(u, v)


#
# Forbidden relative positioning of the pairs of repeated fragments
#
def forbidden_pairing_definition(prob: LpProblem,
                                 var: PuLPVarRepFModelT,
                                 mdcg: MDCGraph):
    """Constraint defining the forbidden pairing cases.

    Parameters
    ----------
    prob : LpProblem
        PuLP problem
    var : PuLPVarInvFModel or PuLPVarDirFModel
        PuLP variables
    mdcg : MDCGraph
        Multiplied doubled contig graph
    """
    for p_repf in type(var).pair_repeat_frag_fn(mdcg):
        for case_ind, u, v, w, x in type(var).forbidden_pairing_fn(p_repf):
            #
            #  u v w x
            # --------->
            #
            prob += (
                3 * var.pairing_ban[case_ind, p_repf[0], p_repf[1]]
                <= var.alpha(u, v)
                + var.alpha(v, w)
                + var.alpha(w, x)
            )
            prob += (
                var.alpha(u, v)
                + var.alpha(v, w)
                + var.alpha(w, x)
                <= 2 + var.pairing_ban[case_ind, p_repf[0], p_repf[1]]
            )
        #
        # Repeated fragments can be paired if they are not implied
        #   in any of the forbidden pairing cases
        #
        prob += (
            var.m[p_repf[0]] + var.m[p_repf[1]]
            <= 2 - lpSum(var.pairing_ban[nested_ind, p_repf[0], p_repf[1]]
                         for nested_ind in range(8))
        )


# ---------------------------------------------------------------------------- #
#                               Repeat Contiguity                              #
# ---------------------------------------------------------------------------- #
def adjacent_fragments(prob: LpProblem,
                       var: PuLPVarRepFModelT,
                       mdcg: MDCGraph):
    """Constraint defining the adjacency of repeated fragments.

    Parameters
    ----------
    prob : LpProblem
        PuLP problem
    var : PuLPVarInvFModel or PuLPVarDirFModel
        PuLP variables
    mdcg : MDCGraph
        Multiplied doubled contig graph
    """
    for u, v in type(var).adj_repeat_frag_fn(mdcg):
        # ik lj or lj ik
        # XXX must take in account that Xik AND Xki can exist simultaneously!
        p, _ = type(var).repeat_frag_builder_fn(u)
        q, _ = type(var).repeat_frag_builder_fn(v)
        #
        # If adjacent, then the first edge is chosen
        #
        prob += var.isadj[u, v] <= var.x[u, v]
        #
        # If adjacent, then the second edge is chosen
        #
        prob += (
            var.isadj[u, v]
            <= var.x[type(var).adj_repeat_other_fn((u, v))]
        )
        #
        # Is adjacent then the first inverted fragment is chosen
        #
        prob += var.isadj[u, v] <= var.m[p]
        #
        # Is adjacent then the second inverted fragment is chosen
        #
        prob += var.isadj[u, v] <= var.m[q]


# ---------------------------------------------------------------------------- #
#                              Speed-up The Model                              #
# ---------------------------------------------------------------------------- #
def occurrences_priority(prob: LpProblem,
                         var: PuLPVarModelT,
                         mdcg: MDCGraph):
    """Constraint for occurrences priority.

    Parameters
    ----------
    prob : LpProblem
        PuLP problem
    var : PuLPVarInvFModel or PuLPVarDirFModel
        PuLP variables
    mdcg : MDCGraph
        Multiplied doubled contig graph
    """
    vertices = mdcg.vertices()
    for u_ind in mdcg.repeated_contigs():
        #
        # Vertices occurrence priority
        #
        for u_occ in range(vertices.attr(u_ind, MULT_ATTR) - 1):
            prob += (
                var.i[(u_ind, FORWARD_INT, u_occ + 1)]
                + var.i[(u_ind, REVERSE_INT, u_occ + 1)]
                <= var.i[(u_ind, FORWARD_INT, u_occ)]
                + var.i[(u_ind, REVERSE_INT, u_occ)]
            )


def pairs_priority(prob: LpProblem,
                   var: PuLPVarRepFModelT,
                   mdcg: MDCGraph):
    """Constraint for pairs priority.

    Parameters
    ----------
    prob : LpProblem
        PuLP problem
    var : PuLPVarInvFModel or PuLPVarDirFModel
        PuLP variables
    mdcg : MDCGraph
        Multiplied doubled contig graph
    """
    for u_ind in mdcg.repeated_contigs():
        #
        # Consecutive pairs of inverted fragments priority
        #
        for p, q in type(var).pair_repeat_consecutive_fn(mdcg, u_ind):
            prob += var.m[q] <= var.m[p]


# ---------------------------------------------------------------------------- #
#                               Keep Old Repeats                               #
# ---------------------------------------------------------------------------- #
def fix_repeats_subpaths(prob: LpProblem, var: PuLPVarPath,
                         fix_result: ScaffoldingResult):
    """Fix subpaths corresponding to repeats.

    Parameters
    ----------
    prob : LpProblem
        PuLP problem
    var : PuLPVarPath
        PuLP variables
    fix_result : ScaffoldingResult
        Previous scaffolding result
    """
    # ------------------------------------------------------------------------ #
    # Inverted repeats
    # ------------------------------------------------------------------------ #
    for ir_ind in fix_result.ir_regions():

        ir_path_iter = fix_result.region_occorc(ir_ind)
        i = next(ir_path_iter)
        j = invf_other(i)
        #
        # The two vertices of the beginner inverted fragment are in the path
        #
        prob += var.i[i] == 1
        prob += var.i[j] == 1

        for k in ir_path_iter:

            l = invf_other(k)
            #
            # The two vertices of the next inverted fragment are in the path
            #
            prob += var.i[k] == 1
            prob += var.i[l] == 1
            #
            # Fix edges of inverted fragments
            #
            prob += var.x[i, k] == 1
            prob += var.x[l, j] == 1

            i = k
            j = l

    # ------------------------------------------------------------------------ #
    # Direct repeats
    # ------------------------------------------------------------------------ #
    for dr_ind in fix_result.dr_regions():

        dr_path_iter = fix_result.region_occorc(dr_ind)
        i = next(dr_path_iter)
        j = dirf_other(i)
        #
        # The two vertices of the beginner direct fragment are in the path
        #
        prob += var.i[i] == 1
        prob += var.i[j] == 1

        for k in dr_path_iter:

            l = dirf_other(k)
            #
            # The two vertices of the next direct fragment are in the path
            #
            prob += var.i[k] == 1
            prob += var.i[l] == 1
            #
            # Fix edges of direct fragments
            #
            prob += var.x[i, k] == 1
            prob += var.x[j, l] == 1

            i = k
            j = l


# ============================================================================ #
#                                   FUNCTIONS                                  #
# ============================================================================ #
def pos(var: PuLPVarRepFModelT, mdcg: MDCGraph,
        vertex: OccOrCT) -> LpAffineExpression:
    """Give the position of vertex in the path.

    Parameters
    ----------
    var : PuLPVarInvFModel or PuLPVarDirFModel
        Variables
    mdcg : MDCGraph
        Multiplied doubled contig graph
    vertex : OccOrCT
        Vertex in MDCGraph

    Returns
    -------
    LpAffineExpression
        Affine expresion interpreted as the position of the vertex in the path
    """
    return lpSum(var.f[vertex, w] for w in mdcg.multiplied_succs(vertex))
