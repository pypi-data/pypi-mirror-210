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
# ---------------------------------------------------------------------------- #
#                                     Sets                                     #
# ---------------------------------------------------------------------------- #
InvFT = tuple[OccOrCT, OccOrCT]
PInvFT = tuple[InvFT, InvFT]

# ---------------------------------------------------------------------------- #
#                                Forbidden Cases                               #
# ---------------------------------------------------------------------------- #
ForbiddenPairInvFT = tuple[IndexT, OccOrCT, OccOrCT, OccOrCT, OccOrCT]


# ============================================================================ #
#                            INVERTED FRAGMENTS SETS                           #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                                     InvF                                     #
# ---------------------------------------------------------------------------- #
def invf(mdcg: MDCGraph) -> Iterator[InvFT]:
    """Iterate on unredundant inverted fragments.

    Parameters
    ----------
    mdcg : MDCGraph
        Multiplied doubled contig graph

    Yields
    ------
    InvFT
        Inverted fragment
    """
    for v_ind in mdcg.repeated_contigs():
        yield from v_invf(mdcg, v_ind)


def v_invf(mdcg: MDCGraph, v_ind: IndexT) -> Iterator[InvFT]:
    """Iterate on inverted fragments of a vertex.

    Parameters
    ----------
    mdcg : MDCGraph
        Multiplied doubled contig graph
    v_ind : IndexT
        Vertex index

    Yields
    ------
    InvFT
        Inverted fragment
    """
    v_mult = mdcg.vertices().attr(v_ind, MULT_ATTR)
    for i in range(0, 2 * (v_mult // 2), 2):
        yield (
            (v_ind, FORWARD_INT, i),
            (v_ind, REVERSE_INT, i + 1),
        )


def invf_builder(v: OccOrCT) -> tuple[InvFT, int]:
    """Inverted fragments builder from vertex.

    Parameters
    ----------
    v : OccOrCT
        Multiplied doubled contig

    Returns
    -------
    InvFT
        Inverted pair associated to vertex
    int
        Position of vertex in built pair

    Notes
    -----
    Requires that :math:`(v_{occ} - v_{or})|2`
    """
    return (
        ((v[CIND_IND], FORWARD_INT, v[COCC_IND] - v[COR_IND]),
         (v[CIND_IND], REVERSE_INT, v[COCC_IND] + (REVERSE_INT - v[COR_IND])),
         ),
        v[COR_IND],
    )


def invf_canonical(v: OccOrCT) -> OccOrCT:
    """Inverted fragment canonical.

    Parameters
    ----------
    v : OccOrCT
        Multiplied oriented contig

    Returns
    -------
    OccOrCT
        Canonical of the inverted fragments

    Notes
    -----
    Requires that :math:`(v_{occ} - v_{or})|2`
    """
    return (v[CIND_IND], FORWARD_INT, v[COCC_IND] - v[COR_IND])


def invf_other(v: OccOrCT) -> OccOrCT:
    """Return the other vertex in the inverted fragments.

    Parameters
    ----------
    v : OccOrCT
        Multiplied oriented contig

    Returns
    -------
    OccOrCT
        The other vertex in the inverted fragments

    Notes
    -----
    Requires that :math:`(v_{occ} - v_{or})|2`
    """
    if v[COR_IND] == REVERSE_INT:
        return (v[CIND_IND], FORWARD_INT, v[COCC_IND] - REVERSE_INT)
    return (v[CIND_IND], REVERSE_INT, v[COCC_IND] + REVERSE_INT)


# ---------------------------------------------------------------------------- #
#                                     PInvF                                    #
# ---------------------------------------------------------------------------- #
def pinvf(mdcg: MDCGraph) -> Iterator[PInvFT]:
    """Iterate on pair of inverted fragments.

    Parameters
    ----------
    mdcg : MDCGraph
        Multiplied doubled contig graph

    Yields
    ------
    PInvFT
        Pair of inverted fragments
    """
    repeated_contigs = mdcg.repeated_contigs()
    for i, v_ind in enumerate(repeated_contigs):
        for p in v_invf(mdcg, v_ind):
            # same vertex index
            for q in v_invf(mdcg, v_ind):
                if p[REVERSE_INT][COCC_IND] < q[FORWARD_INT][COCC_IND]:
                    yield p, q
            # superior vertex index
            for j in range(i + 1, len(repeated_contigs)):
                for q in v_invf(mdcg, repeated_contigs[j]):
                    yield p, q


# ---------------------------------------------------------------------------- #
#                                     AInvF                                    #
# ---------------------------------------------------------------------------- #
def ainvf(mdcg: MDCGraph) -> Iterator[EOccOrCT]:
    """Iterate on inverted fragments successors.

    Parameters
    ----------
    mdcg : MDCGraph
        Multiplied doubled contigs graph

    Yields
    ------
    EOccOrCT
        Canonical edges between two inverted fragments
    """
    for u_ind in mdcg.repeated_contigs():
        u_mult = mdcg.vertices().attr(u_ind, MULT_ATTR)
        yield from __ainvf_succs_f(mdcg, u_ind, u_mult)
        yield from __ainvf_succs_r(mdcg, u_ind, u_mult)


def __ainvf_succs_f(mdcg: MDCGraph,
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
        Canonical edges between two inverted fragments
    """
    # DOCU explain this
    for (v_ind, v_or), _ in mdcg.edges().succs((u_ind, FORWARD_INT)):
        if u_ind < v_ind:
            v_mult = mdcg.vertices().attr(v_ind, MULT_ATTR)
            for u_occ in range(0, 2 * (u_mult // 2), 2):
                for v_occ in range(0, 2 * (v_mult // 2), 2):
                    yield (
                        (u_ind, FORWARD_INT, u_occ),
                        (v_ind, v_or, v_occ + v_or),
                    )
        elif u_ind == v_ind:
            for u_occ in range(0, 2 * (u_mult // 2) - 2, 2):
                for v_occ in range(u_occ + 2, 2 * (u_mult // 2), 2):
                    yield (
                        (u_ind, FORWARD_INT, u_occ),
                        (u_ind, v_or, v_occ + v_or),
                    )


def __ainvf_succs_r(mdcg: MDCGraph,
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
        Canonical edges between two inverted fragments
    """
    # DOCU explain this
    for (w_ind, w_or), _ in mdcg.edges().succs((u_ind, REVERSE_INT)):
        if u_ind < w_ind:
            w_mult = mdcg.vertices().attr(w_ind, MULT_ATTR)
            for u_occ in range(0, 2 * (u_mult // 2), 2):
                for w_occ in range(0, 2 * (w_mult // 2), 2):
                    yield (
                        (u_ind, REVERSE_INT, u_occ + REVERSE_INT),
                        (w_ind, w_or, w_occ + w_or),
                    )
        elif u_ind == w_ind and w_or == FORWARD_INT:
            for u_occ in range(0, 2 * (u_mult // 2) - 2, 2):
                for w_occ in range(u_occ + 2, 2 * (u_mult // 2), 2):
                    yield (
                        (u_ind, REVERSE_INT, u_occ),
                        (u_ind, FORWARD_INT, w_occ),
                    )


def ainvf_other(edge: EOccOrCT) -> EOccOrCT:
    """Get the pairing edge.

    Parameters
    ----------
    edge : EOccOrCT
        Edge between two inverted fragments

    Returns
    -------
    EOccOrCT
        The other edge between the two inverted fragments
    """
    return invf_other(edge[1]), invf_other(edge[0])


# ---------------------------------------------------------------------------- #
#                               Consecutive PInvF                              #
# ---------------------------------------------------------------------------- #
def consecutive_pinvf(mdcg: MDCGraph, v_ind: IndexT) -> Iterator[PInvFT]:
    """Iterate over consecutive pairs of inverted fragments.

    Parameters
    ----------
    mdcg : MDCGraph
        Multiplied doubled contig graph
    v_ind : IndexT
        Vertex' index

    Yields
    ------
    PInvFT
        Consecutive pairs of inverted fragments
    """
    mult_v = mdcg.vertices().attr(v_ind, MULT_ATTR)
    for (i, j) in v_invf(mdcg, v_ind):
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
def pinvf_alpha(mdcg: MDCGraph) -> Iterator[EOccOrCT]:
    """Iterate on alpha keys for inverted fragments pairs.

    Parameters
    ----------
    mdcg : MDCGraph
        Multiplied doubled contig graph

    Yields
    ------
    EOccOrCT
        Alpha key set's element
    """
    for (i, j), (k, l) in pinvf(mdcg):
        yield i, k
        yield i, l
        yield j, k
        yield j, l


def forbidden_intersection(p_invf: PInvFT) -> Iterator[ForbiddenPairInvFT]:
    """Iterate over the forbidden cases.

    Parameters
    ----------
    p_invf : PInvFT
        Pair of inverted fragments

    Yields
    ------
    ForbiddenPairInvFT
        Forbidden pairing cases for inverted fragments,
        enriched with an index
    """
    (i, j), (k, l) = p_invf
    yield 0, i, k, j, l
    yield 1, i, l, j, k
    yield 2, j, k, i, l
    yield 3, j, l, i, k
    yield 4, k, i, l, j
    yield 5, k, j, l, i
    yield 6, l, i, k, j
    yield 7, l, j, k, i
