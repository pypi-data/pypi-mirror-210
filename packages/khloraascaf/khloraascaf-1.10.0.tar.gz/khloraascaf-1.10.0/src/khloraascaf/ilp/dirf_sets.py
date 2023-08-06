# -*- coding=utf-8 -*-

"""Set definitions for ILP invf model."""


from typing import Iterator

from revsymg.index_lib import FORWARD_INT, REVERSE_INT

from khloraascaf.inputs import MultT
from khloraascaf.multiplied_doubled_contig_graph import (
    CIND_IND,
    COCC_IND,
    COR_IND,
    MULT_ATTR,
    EOccOrCT,
    IndexT,
    MDCGraph,
    OccOrCT,
)


# ============================================================================ #
#                                     TYPES                                    #
# ============================================================================ #
DirFT = tuple[OccOrCT, OccOrCT]
PDirFT = tuple[DirFT, DirFT]

# ---------------------------------------------------------------------------- #
#                                Forbidden Cases                               #
# ---------------------------------------------------------------------------- #
ForbiddenPairDirFT = tuple[IndexT, OccOrCT, OccOrCT, OccOrCT, OccOrCT]


# ============================================================================ #
#                             DIRECT FRAGMENTS SETS                            #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                                     DirF                                     #
# ---------------------------------------------------------------------------- #
def dirf(mdcg: MDCGraph) -> Iterator[DirFT]:
    """Iterate on unredundant direct fragments.

    Parameters
    ----------
    mdcg : MDCGraph
        Multiplied doubled contig graph

    Yields
    ------
    DirFT
        Direct fragment
    """
    for v_ind in mdcg.repeated_contigs():
        yield from v_dirf(mdcg, v_ind)


def v_dirf(mdcg: MDCGraph, v_ind: IndexT) -> Iterator[DirFT]:
    """Iterate on direct fragments of a vertex.

    Parameters
    ----------
    mdcg : MDCGraph
        Multiplied doubled contig graph
    v_ind : IndexT
        Vertex index

    Yields
    ------
    DirFT
        Direct fragment
    """
    v_mult = mdcg.vertices().attr(v_ind, MULT_ATTR)
    for i in range(0, 2 * (v_mult // 2), 2):
        yield (
            (v_ind, FORWARD_INT, i),
            (v_ind, FORWARD_INT, i + 1),
        )
        yield (
            (v_ind, REVERSE_INT, i),
            (v_ind, REVERSE_INT, i + 1),
        )


def dirf_builder(v: OccOrCT) -> tuple[DirFT, int]:
    """Direct fragments builder from vertex.

    Parameters
    ----------
    v : OccOrCT
        Multiplied doubled contig

    Returns
    -------
    DirFT
        Direct fragment associated to vertex
    int
        Position of vertex in built direct fragments
    """
    rest = v[COCC_IND] % 2
    return (
        (
            (v[CIND_IND], v[COR_IND], v[COCC_IND] - rest),
            (v[CIND_IND], v[COR_IND], v[COCC_IND] + (1 - rest)),
        ),
        rest,
    )


def dirf_canonical(v: OccOrCT) -> OccOrCT:
    """Direct fragment canonical.

    Parameters
    ----------
    v : OccOrCT
        Multiplied oriented contig

    Returns
    -------
    OccOrCT
        Canonical of the direct fragments
    """
    return (v[CIND_IND], v[COR_IND], v[COCC_IND] - v[COCC_IND] % 2)


def dirf_other(v: OccOrCT) -> OccOrCT:
    """Return the other vertex in the direct fragments.

    Parameters
    ----------
    v : OccOrCT
        Multiplied oriented contig

    Returns
    -------
    OccOrCT
        The other vertex in the direct fragments
    """
    if v[COCC_IND] % 2 == 1:
        return (v[CIND_IND], v[COR_IND], v[COCC_IND] - 1)
    return (v[CIND_IND], v[COR_IND], v[COCC_IND] + 1)


# ---------------------------------------------------------------------------- #
#                                     PDirF                                    #
# ---------------------------------------------------------------------------- #
def pdirf(mdcg: MDCGraph) -> Iterator[PDirFT]:
    """Iterate on pair of direct fragments.

    Parameters
    ----------
    mdcg : MDCGraph
        Multiplied doubled contig graph

    Yields
    ------
    PInvFT
        Pair of direct fragments
    """
    repeated_contigs = mdcg.repeated_contigs()
    for i, v_ind in enumerate(repeated_contigs):
        for p in v_dirf(mdcg, v_ind):
            # same vertex index
            for q in v_dirf(mdcg, v_ind):
                if p[REVERSE_INT][COCC_IND] < q[FORWARD_INT][COCC_IND]:
                    yield p, q
            # superior vertex index
            for j in range(i + 1, len(repeated_contigs)):
                for q in v_dirf(mdcg, repeated_contigs[j]):
                    yield p, q


# ---------------------------------------------------------------------------- #
#                                     ADirF                                    #
# ---------------------------------------------------------------------------- #
def adirf(mdcg: MDCGraph) -> Iterator[EOccOrCT]:
    """Iterate on direct fragments successors.

    Parameters
    ----------
    mdcg : MDCGraph
        Multiplied doubled contigs graph

    Yields
    ------
    EOccOrCT
        Canonical edges between two direct fragments
    """
    for u_ind in mdcg.repeated_contigs():
        u_mult = mdcg.vertices().attr(u_ind, MULT_ATTR)
        yield from __adirf_succs_f(mdcg, u_ind, u_mult)
        yield from __adirf_succs_r(mdcg, u_ind, u_mult)


def __adirf_succs_f(mdcg: MDCGraph,
                    u_ind: IndexT, u_mult: MultT) -> Iterator[EOccOrCT]:
    """Iterate of successors of forward vertex.

    Parameters
    ----------
    mdcg : MDCGraph
        Multiplied doubled contigs graph
    u_ind : IndexT
        Vertex identifier
    u_mult : MultT
        Vertex multiplicity

    Yields
    ------
    EOccOrCT
        Canonical edges between two direct fragments
    """
    # DOCU explain this
    for (v_ind, v_or), _ in mdcg.edges().succs((u_ind, FORWARD_INT)):
        #
        # Accept u_f -> v_f and u_f -> v_r
        # Will accept v_f -> u_f and v_f -> u_r
        #
        if u_ind != v_ind:
            v_mult = mdcg.vertices().attr(v_ind, MULT_ATTR)
            for u_occ in range(0, 2 * (u_mult // 2), 2):
                for v_occ in range(0, 2 * (v_mult // 2), 2):
                    yield (
                        (u_ind, FORWARD_INT, u_occ),
                        (v_ind, v_or, v_occ),
                    )
        #
        # Accept u_f -> u_f and u_f -> u_r
        #
        elif u_ind == v_ind:
            for u_occ in range(0, 2 * (u_mult // 2) - 2, 2):
                for v_occ in range(u_occ + 2, 2 * (u_mult // 2), 2):
                    yield (
                        (u_ind, FORWARD_INT, u_occ),
                        (u_ind, v_or, v_occ),
                    )


def __adirf_succs_r(mdcg: MDCGraph,
                    u_ind: IndexT, u_mult: MultT) -> Iterator[EOccOrCT]:
    """Iterate of successors of reverse vertex.

    Parameters
    ----------
    mdcg : MDCGraph
        Multiplied doubled contigs graph
    u_ind : IndexT
        Vertex identifier
    u_mult : MultT
        Vertex multiplicity

    Yields
    ------
    EOccOrCT
        Canonical edges between two direct fragments
    """
    # DOCU explain this
    for (w_ind, w_or), _ in mdcg.edges().succs((u_ind, REVERSE_INT)):
        #
        # Accept u_r -> w_f and u_r -> w_r
        # Will accept w_r -> u_f and w_r -> u_r
        #
        if u_ind != w_ind:
            w_mult = mdcg.vertices().attr(w_ind, MULT_ATTR)
            for u_occ in range(0, 2 * (u_mult // 2), 2):
                for w_occ in range(0, 2 * (w_mult // 2), 2):
                    yield (
                        (u_ind, REVERSE_INT, u_occ),
                        (w_ind, w_or, w_occ),
                    )
        #
        # Accept u_r -> u_f
        #
        elif u_ind == w_ind and w_or == FORWARD_INT:
            for u_occ in range(0, 2 * (u_mult // 2) - 2, 2):
                for w_occ in range(u_occ + 2, 2 * (u_mult // 2), 2):
                    yield (
                        (u_ind, REVERSE_INT, u_occ),
                        (u_ind, FORWARD_INT, w_occ),
                    )


def adirf_other(edge: EOccOrCT) -> EOccOrCT:
    """Get the pairing edge.

    Parameters
    ----------
    edge : EOccOrCT
        Edge between two direct fragments

    Returns
    -------
    EOccOrCT
        The other edge between the two direct fragments
    """
    return dirf_other(edge[0]), dirf_other(edge[1])


# ---------------------------------------------------------------------------- #
#                               Consecutive PDirF                              #
# ---------------------------------------------------------------------------- #
def consecutive_pdirf(mdcg: MDCGraph, v_ind: IndexT) -> Iterator[PDirFT]:
    """Iterate over consecutive pairs of direct fragments.

    Parameters
    ----------
    mdcg : MDCGraph
        Multiplied doubled contig graph
    v_ind : IndexT
        Vertex' index

    Yields
    ------
    PDirFT
        Consecutive pairs of direct fragments
    """
    mult_v = mdcg.vertices().attr(v_ind, MULT_ATTR)
    for (i, j) in v_dirf(mdcg, v_ind):
        if j[COCC_IND] + 2 < mult_v:
            yield (
                (i, j),
                (
                    (i[CIND_IND], i[COR_IND], i[COCC_IND] + 2),
                    (j[CIND_IND], j[COR_IND], j[COCC_IND] + 2),
                ),
            )


# ============================================================================ #
#                               FORBIDDEN PAIRING                              #
# ============================================================================ #
def pdirf_alpha(mdcg: MDCGraph) -> Iterator[EOccOrCT]:
    """Iterate on alpha keys for direct fragments pairs.

    Parameters
    ----------
    mdcg : MDCGraph
        Multiplied doubled contig graph

    Yields
    ------
    EOccOrCT
        Alpha key set's element
    """
    # OPTIMIZE reduce loop redundancies in keys
    for (i, j), (k, l) in pdirf(mdcg):
        yield i, j  # . i j . or . j i .
        yield k, l  # . k l . or . l k .
        yield i, k  # i k l j or k i j l or l j i k or j l k i
        yield j, l
        yield i, l  # i l k j or l i j k or k j i l or j k l i
        yield j, k


def forbidden_nested(p_dirf: PDirFT) -> Iterator[ForbiddenPairDirFT]:
    """Iterate over the forbidden cases.

    Parameters
    ----------
    p_dirf : PDirFT
        Pair of direct fragments

    Yields
    ------
    ForbiddenPairDirFT
        Forbidden pairing cases for direct fragments,
        enriched with an index
    """
    (i, j), (k, l) = p_dirf
    # Forbidden order    # Alpha keys
    # ----------------------------------
    yield 0, i, k, l, j  # i k  k l  j l
    yield 1, i, l, k, j  # i l  k l  j k
    yield 2, j, k, l, i  # j k  k l  i l
    yield 3, j, l, k, i  # j l  k l  i k
    yield 4, k, i, j, l  # i k  i j  j l
    yield 5, k, j, i, l  # j k  i j  i l
    yield 6, l, i, j, k  # i l  i j  j k
    yield 7, l, j, i, k  # j l  i j  i k
