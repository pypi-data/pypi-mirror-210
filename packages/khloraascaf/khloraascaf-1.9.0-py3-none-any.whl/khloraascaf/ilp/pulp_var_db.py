# -*- coding=utf-8 -*-

"""The PuLPVarDB classes file."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Union

from pulp import LpBinary, LpContinuous, LpVariable
from pulp.pulp import LpAffineExpression
from revsymg.index_lib import IndexT

from khloraascaf.ilp.dirf_sets import (
    DirFT,
    adirf,
    adirf_other,
    consecutive_pdirf,
    dirf,
    dirf_builder,
    forbidden_nested,
    pdirf,
    pdirf_alpha,
)
from khloraascaf.ilp.invf_sets import (
    InvFT,
    ainvf,
    ainvf_other,
    consecutive_pinvf,
    forbidden_intersection,
    invf,
    invf_builder,
    pinvf,
    pinvf_alpha,
)
from khloraascaf.multiplied_doubled_contig_graph import (
    CIND_IND,
    COCC_IND,
    EOccOrCT,
    MDCGraph,
    OccOrCT,
)


# DOCU sphinx doc pulp var db
# ============================================================================ #
#                                   CONSTANTS                                  #
# ============================================================================ #
BIN_THRESHOLD = 0.5


# ============================================================================ #
#                                     TYPES                                    #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                                Path Variables                                #
# ---------------------------------------------------------------------------- #
DiVarT = dict[OccOrCT, LpVariable]
DxVarT = dict[EOccOrCT, LpVariable]
DfVarT = dict[EOccOrCT, LpVariable]

# ---------------------------------------------------------------------------- #
#                                InvF Variables                                #
# ---------------------------------------------------------------------------- #
DmInvFVarT = dict[InvFT, LpVariable]
DintersVarT = dict[tuple[IndexT, InvFT, InvFT], LpVariable]

# ---------------------------------------------------------------------------- #
#                                DirF Variables                                #
# ---------------------------------------------------------------------------- #
DmDirFVarT = dict[DirFT, LpVariable]
DnestedVarT = dict[tuple[int, DirFT, DirFT], LpVariable]

# ---------------------------------------------------------------------------- #
#                                Alpha Variables                               #
# ---------------------------------------------------------------------------- #
DalphaVarT = dict[EOccOrCT, LpVariable]

# ---------------------------------------------------------------------------- #
#                              Adjacent Fragments                              #
# ---------------------------------------------------------------------------- #
DisadjVarT = dict[EOccOrCT, LpVariable]


# ============================================================================ #
#                        PULP VARIABLE DATA BASE CLASSES                       #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                                 Base Classes                                 #
# ---------------------------------------------------------------------------- #
@dataclass
class PuLPVarPath():
    """Data class for necessary variables to modelise a path."""

    def __init__(self, mdcg: MDCGraph, starter_vertex: OccOrCT):
        """The Initializer."""
        self.i: DiVarT = {
            v: LpVariable(f'i_{v}', cat=LpContinuous)
            for v in mdcg.multiplied_vertices()
            if v[CIND_IND] != starter_vertex[CIND_IND]
        }
        self.x: DxVarT = {
            e: LpVariable(f'x_{e}', cat=LpBinary)
            for e in mdcg.multiplied_edges()
        }
        self.f: DfVarT = {
            e: LpVariable(f'f_{e}', lowBound=0, cat=LpContinuous)
            for e in mdcg.multiplied_edges()
        }


@dataclass
class PuLPVarInvF():
    """Data class for necessary variables to modelise inverted fragments."""

    repeat_frag_fn = invf
    repeat_frag_builder_fn = invf_builder
    pair_repeat_alpha_fn = pinvf_alpha
    pair_repeat_frag_fn = pinvf
    pair_repeat_consecutive_fn = consecutive_pinvf
    adj_repeat_frag_fn = ainvf
    adj_repeat_other_fn = ainvf_other
    forbidden_pairing_fn = forbidden_intersection

    def __init__(self, mdcg: MDCGraph):
        """The Initializer."""
        self.m: DmInvFVarT = {
            p: LpVariable(f'm_{p}', cat=LpBinary)
            for p in PuLPVarInvF.repeat_frag_fn(mdcg)
        }
        self._alpha: DalphaVarT = {
            (u, v): LpVariable(f'alpha_{u}_{v}', cat=LpBinary)
            for u, v in PuLPVarInvF.pair_repeat_alpha_fn(mdcg)
        }
        self.pairing_ban: DintersVarT = {
            (k, p, q): LpVariable(f'forbid_{k}_{p}_{q}', cat=LpBinary)
            for p, q in PuLPVarInvF.pair_repeat_frag_fn(mdcg)
            for k in range(8)
        }
        self.isadj: DisadjVarT = {
            (u, v): LpVariable(f'isadj_{u}_{v}', cat=LpBinary)
            for u, v in PuLPVarInvF.adj_repeat_frag_fn(mdcg)
        }

    def alpha(self, u: OccOrCT, v: OccOrCT) -> LpAffineExpression:
        r"""Return alpha variable according to u and v.

        Parameters
        ----------
        u : OccOrCT
            Multiplied oriented contig u
        v : OccOrCT
            Multiplied oriented contig v

        Returns
        -------
        LpAffineExpression
            binary variable alpha

        Notes
        -----
        Define that :math:`\alpha_{uv} = 1 - \alpha_{vu}`
        using only one :math:`(u, v)` pair key
        """
        if alpha_key(u, v):
            return self._alpha[u, v]
        return 1 - self._alpha[v, u]

    def invf_solution(self) -> Iterator[InvFT]:
        """Iterate over the inverted fragments solution.

        Yields
        ------
        InvFT
            Inverted fragments solution
        """
        for p, var_p in self.m.items():
            if var_p.value() > BIN_THRESHOLD:
                yield p


@dataclass
class PuLPVarDirF():
    """Data class for necessary variables to modelise direct fragments."""

    repeat_frag_fn = dirf
    repeat_frag_builder_fn = dirf_builder
    pair_repeat_alpha_fn = pdirf_alpha
    pair_repeat_frag_fn = pdirf
    pair_repeat_consecutive_fn = consecutive_pdirf
    adj_repeat_frag_fn = adirf
    adj_repeat_other_fn = adirf_other
    forbidden_pairing_fn = forbidden_nested

    def __init__(self, mdcg: MDCGraph):
        """The Initializer."""
        self.m: DmDirFVarT = {
            p: LpVariable(f'm_{p}', cat=LpBinary)
            for p in PuLPVarDirF.repeat_frag_fn(mdcg)
        }
        self._alpha: DalphaVarT = {
            (u, v): LpVariable(f'alpha_{u}_{v}', cat=LpBinary)
            for u, v in PuLPVarDirF.pair_repeat_alpha_fn(mdcg)
        }
        self.pairing_ban: DnestedVarT = {
            (k, p, q): LpVariable(f'forbid_{k}_{p}_{q}', cat=LpBinary)
            for k in range(8)
            for p, q in PuLPVarDirF.pair_repeat_frag_fn(mdcg)
        }
        self.isadj: DisadjVarT = {
            (u, v): LpVariable(f'isadj_{u}_{v}', cat=LpBinary)
            for u, v in PuLPVarDirF.adj_repeat_frag_fn(mdcg)
        }

    def alpha(self, u: OccOrCT, v: OccOrCT) -> LpAffineExpression:
        r"""Return alpha variable according to u and v.

        Parameters
        ----------
        u : OccOrCT
            Multiplied oriented contig u
        v : OccOrCT
            Multiplied oriented contig v

        Returns
        -------
        LpAffineExpression
            binary variable alpha

        Notes
        -----
        Define that :math:`\alpha_{uv} = 1 - \alpha_{vu}`
        using only one :math:`(u, v)` pair key
        """
        if alpha_key(u, v):
            return self._alpha[u, v]
        return 1 - self._alpha[v, u]

    def dirf_solution(self) -> Iterator[DirFT]:
        """Iterate over the direct fragments solution.

        Yields
        ------
        DirFT
            Direct fragments solution
        """
        for p, var_p in self.m.items():
            if var_p.value() > BIN_THRESHOLD:
                yield p


# ---------------------------------------------------------------------------- #
#                                 Model Classes                                #
# ---------------------------------------------------------------------------- #
@dataclass
class PuLPVarInvFModel(PuLPVarPath, PuLPVarInvF):
    """Data class for necessary variables to modelise invf model."""

    def __init__(self, mdcg: MDCGraph, starter_vertex: OccOrCT):
        PuLPVarPath.__init__(self, mdcg, starter_vertex)
        PuLPVarInvF.__init__(self, mdcg)


@dataclass
class PuLPVarDirFModel(PuLPVarPath, PuLPVarDirF):
    """Data class for necessary variables to modelise dirf model."""

    def __init__(self, mdcg: MDCGraph, starter_vertex: OccOrCT):
        PuLPVarPath.__init__(self, mdcg, starter_vertex)
        PuLPVarDirF.__init__(self, mdcg)


@dataclass
class PuLPVarPresScoreModel(PuLPVarPath):
    """Data class for necessary variables to modelise presscore model."""

    def __init__(self, mdcg: MDCGraph, starter_vertex: OccOrCT):
        PuLPVarPath.__init__(self, mdcg, starter_vertex)


PuLPVarRepFModelT = Union[PuLPVarInvFModel, PuLPVarDirFModel]
PuLPVarModelT = Union[PuLPVarRepFModelT, PuLPVarPresScoreModel]


# ============================================================================ #
#                                ALPHA VARIABLES                               #
# ============================================================================ #
def alpha_key(u: OccOrCT, v: OccOrCT) -> bool:
    """Return the oriented unredondant (u, v) alpha key.

    Parameters
    ----------
    u : OccOrCT
        Multiplied oriented contig
    v : OccOrCT
        Multiplied oriented contig

    Returns
    -------
    bool
        True if (u, v) is an alpha key, False if (v, u) is an alpha key

    Raises
    ------
    KeyError
        If there is no key with u, v couple in alpha key set
    """
    if u[CIND_IND] < v[CIND_IND]:
        return True
    if u[CIND_IND] > v[CIND_IND]:
        return False
    # case u_id = v_id
    if u[COCC_IND] < v[COCC_IND]:
        return True
    if u[COCC_IND] > v[COCC_IND]:
        return False
    raise KeyError
