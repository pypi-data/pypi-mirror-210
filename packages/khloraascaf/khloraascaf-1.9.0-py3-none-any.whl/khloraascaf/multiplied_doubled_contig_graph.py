# -*- coding=utf-8 -*-

"""Un-redondant contig graph module."""


from pathlib import Path
from typing import Iterator, Literal

from revsymg.graphs import RevSymGraph
from revsymg.index_lib import FORWARD_INT, ORIENT_REV, IndexT, OrT

from khloraascaf.inputs import (
    MULT_UPB_DEF,
    PRESSCORE_UPB_DEF,
    IdCT,
    MultT,
    PresScoreT,
    read_contig_attributes,
    read_contig_links_file,
)


# DOCU missing constant docstrings
# ============================================================================ #
#                                     TYPES                                    #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                                    Indexed                                   #
# ---------------------------------------------------------------------------- #
OccOrCT = tuple[IndexT, OrT, IndexT]
EOccOrCT = tuple[OccOrCT, OccOrCT]


# ============================================================================ #
#                                   CONSTANTS                                  #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                                    Indices                                   #
# ---------------------------------------------------------------------------- #
#
# For OccOrCT type
#
CIND_IND: Literal[0] = 0
COR_IND: Literal[1] = 1
COCC_IND: Literal[2] = 2

# ---------------------------------------------------------------------------- #
#                                  Attributes                                  #
# ---------------------------------------------------------------------------- #
MULT_ATTR = 'multiplicity'
PRESSCORE_ATTR = 'presence_score'
CTG_ID_ATTR = 'contig_id'
LINK_ID_ATTR = 'link_id'


# ============================================================================ #
#                                     CLASS                                    #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                        Multiplied Doubled Contig Graph                       #
# ---------------------------------------------------------------------------- #
class MDCGraph(RevSymGraph):
    """MDCGraph object.

    DOCU update MDCGraph's doc
    """

    def __init__(self, mult_upb: MultT = MULT_UPB_DEF,
                 presscore_upb: PresScoreT = PRESSCORE_UPB_DEF):
        super().__init__()
        #
        # List of v_ind | v_mult > 1
        #
        self.__repeated_contigs: list[IndexT] = []
        #
        # New attributes
        #
        self._vertices.new_attr(MULT_ATTR, mult_upb)
        self._vertices.new_attr(PRESSCORE_ATTR, presscore_upb)

    # ~*~ Dynamics ~*~

    def add_multiplied_vertex(self, mult: MultT,
                              presence_score: PresScoreT) -> IndexT:
        """Add a vertex.

        Parameters
        ----------
        mult : MultT
            Contig's multiplicity
        presence_score : PresScoreT
            Contig's presence score

        Returns
        -------
        IndexT
            Contig's index
        """
        contig_ind = self._vertices.add()
        self._vertices.set_attr(contig_ind, MULT_ATTR, mult)
        self._vertices.set_attr(contig_ind, PRESSCORE_ATTR, presence_score)
        if mult > 1:
            self.__add_repeated_contig(contig_ind)
        return contig_ind

    # ~*~ Iterators ~*~

    def multiplied_vertices(self) -> Iterator[OccOrCT]:
        """Iterate over the multiplied oriented contigs.

        Yields
        ------
        OccOrCT
            Multiplied oriented contig
        """
        for v_ind, v_or in self._vertices:
            for occ in range(self._vertices.attr(v_ind, MULT_ATTR)):
                yield v_ind, v_or, occ

    def multiplied_edges(self) -> Iterator[EOccOrCT]:
        """Iterate on edges of OccOrCT type.

        Yields
        ------
        EOccOrCT
            Edge of multiplied oriented contigs
        """
        for v_ind, v_or in self._vertices:
            v_mult = self._vertices.attr(v_ind, MULT_ATTR)
            for (w_ind, w_or), _ in self._edges.succs((v_ind, v_or)):
                w_mult = self._vertices.attr(w_ind, MULT_ATTR)
                for v_occ in range(v_mult):
                    for w_occ in range(w_mult):
                        yield (
                            (v_ind, v_or, v_occ),
                            (w_ind, w_or, w_occ),
                        )

    def multiplied_preds(self, v: OccOrCT) -> Iterator[OccOrCT]:
        """Iterate on the OccOrCT predecessors of `v`.

        Parameters
        ----------
        v : OccOrCT
            Multiplied oriented contig

        Yield
        -----
        OccOrCT
            Multiplied oriented predecessors
        """
        for (u_ind, u_or), _ in self._edges.preds((v[CIND_IND], v[COR_IND])):
            u_mult = self._vertices.attr(u_ind, MULT_ATTR)
            for u_occ in range(u_mult):
                yield u_ind, u_or, u_occ

    def multiplied_succs(self, v: OccOrCT) -> Iterator[OccOrCT]:
        """Iterate on the OccOrCT successors of `v`.

        Parameters
        ----------
        v : OccOrCT
            Multiplied oriented contig

        Yield
        -----
        OccOrCT
            Multiplied oriented sucessors
        """
        for (w_ind, w_or), _ in self._edges.succs((v[CIND_IND], v[COR_IND])):
            w_mult = self._vertices.attr(w_ind, MULT_ATTR)
            for w_occ in range(w_mult):
                yield w_ind, w_or, w_occ

    # ~*~ Getter ~*~

    def repeated_contigs(self) -> list[IndexT]:
        """Return the list of repeated contigs' indices.

        Returns
        -------
        list of IndexT
            List of repeated contigs' indices

        Note
        ----
        The list is sorted
        """
        return self.__repeated_contigs

    def multiplied_card(self) -> int:
        """The number of multiplied oriented contig.

        Returns
        -------
        int
            The number of vertices in multiplied doubled contig graph
        """
        return 2 * sum(
            self._vertices.attr(v_ind, MULT_ATTR)
            for v_ind in range(self._vertices.card_index())
        )

    # ~*~ Private ~*~

    def __add_repeated_contig(self, v_ind: IndexT):
        """Add the contig index in the repeat list.

        Parameters
        ----------
        v_ind : IndexT
            Contig's index

        Note
        ----
        For all i < j, repeated_contigs[i] < repeated_contigs[j]
        """
        self.__repeated_contigs.append(v_ind)


# ---------------------------------------------------------------------------- #
#                 Identifier Container Associated With MDCGraph                #
# ---------------------------------------------------------------------------- #
class MDCGraphIDContainer():
    """Container for identifiers linked to MDCgraph object.

    For each vertex' and edge' index in the graph is respectively associated
    a contig' and a link' identifier.
    """

    __NULL_ID: IdCT = ''

    def __init__(self):
        """The Initializer."""
        #
        # Contigs
        #
        #   forward contig indices (there is no index for the reverse)
        self.__contig_to_vertex: dict[IdCT, IndexT] = {}
        #   identifiers associated with vertex's index
        self.__vertex_to_contig: list[IdCT] = []
        #
        # Links
        #
        #   forward link indices (there is no index for the reverse)
        self.__edge_to_link: list[IdCT] = []

    # ~*~ Setter ~*~

    def associate_contig_vertex(self, contig_id: IdCT, vertex_ind: IndexT):
        """Associate the contig with the vertex.

        Parameters
        ----------
        contig_id : IdCT
            Contig's identifier
        vertex_ind : IndexT
            Vertex' index
        """
        self.__contig_to_vertex[contig_id] = vertex_ind
        while vertex_ind > len(self.__vertex_to_contig) - 1:
            self.__vertex_to_contig.append(self.__NULL_ID)
        self.__vertex_to_contig[vertex_ind] = contig_id

    def associate_link_edge(self, link_id: IdCT, edge_ind: IndexT):
        """Associate the link with the edge.

        Parameters
        ----------
        link_id : IdCT
            Link's identifier
        edge_ind : IndexT
            Edge's index
        """
        while edge_ind > len(self.__edge_to_link) - 1:
            self.__edge_to_link.append(self.__NULL_ID)
        self.__edge_to_link[edge_ind] = link_id

    # ~*~ Getter ~*~

    def contig_to_vertex(self, contig_id: IdCT) -> IndexT:
        """Returns the vertex index associated with the contig's id.

        Parameters
        ----------
        contig_id : IdCT
            Contig's identifier

        Returns
        -------
        IndexT
            Vertex' index
        """
        return self.__contig_to_vertex[contig_id]

    def vertex_to_contig(self, vertex_ind: IndexT) -> IdCT:
        """Returns the contig's id associated with the vertex index.

        Parameters
        ----------
        vertex_ind : IndexT
            Vertex' index

        Returns
        -------
        IdCT
            Contig's identifier
        """
        return self.__vertex_to_contig[vertex_ind]

    def edge_to_link(self, edge_index: IndexT) -> IdCT:
        """Returns the link's id associated with the edge index.

        Parameters
        ----------
        edge_index : IndexT
            Edge's index

        Returns
        -------
        IdCT
            Link's identifier
        """
        return self.__edge_to_link[edge_index]


# ============================================================================ #
#                                   FUNCTIONS                                  #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                                Type Operation                                #
# ---------------------------------------------------------------------------- #
def rev_occorc(v: OccOrCT) -> OccOrCT:
    """Return the reverse orientation of v.

    Parameters
    ----------
    v : OccOrCT
        Multiplied oriented contig

    Returns
    -------
    OccOrCT
        Reverse of the multiplied oriented contig
    """
    return v[CIND_IND], ORIENT_REV[v[COR_IND]], v[COCC_IND]


def first_forward_occurrence(vertex_index: IndexT) -> OccOrCT:
    """Returns the first forward occurrence with given vertex index.

    Parameters
    ----------
    vertex_index : IndexT
        Contig's index

    Returns
    -------
    OccOrCT
        The first occurrence, in forward orientation with the given vertex index
    """
    return vertex_index, FORWARD_INT, 0


# ---------------------------------------------------------------------------- #
#                                 Constructors                                 #
# ---------------------------------------------------------------------------- #
def mdcg_with_id_from_input_files(
    contig_attrs: Path,
    contig_links: Path,
    multiplicity_upperbound: MultT = MULT_UPB_DEF,
    presence_score_upperbound: PresScoreT = PRESSCORE_UPB_DEF) -> (
        tuple[MDCGraph, MDCGraphIDContainer]):
    """Instantiate a graph with identifiers from input files.

    Parameters
    ----------
    contig_attrs : Path
        Contigs' attributes file path
    contig_links : Path
        Contigs' links file path
    multiplicity_upperbound : MultT, optional
        Multiplicities upper bound, by default MULT_UPB_DEF
    presence_score_upperbound : PresScoreT, optional
        Multiplicities upper bound, by default MULT_UPB_DEF

    Returns
    -------
    MDCGraph
        Multiplied doubled contig graph
    MDCGraphIDContainer
        Identifiers container for the graph
    """
    mdcg = MDCGraph(
        mult_upb=multiplicity_upperbound,
        presscore_upb=presence_score_upperbound,
    )
    id_container = MDCGraphIDContainer()

    for contig_id, mult, presscore in read_contig_attributes(contig_attrs):
        id_container.associate_contig_vertex(
            contig_id,
            mdcg.add_multiplied_vertex(mult, presscore),
        )

    for l_id, c_id, c_or, d_id, d_or in read_contig_links_file(contig_links):
        id_container.associate_link_edge(
            l_id,
            mdcg.edges().add(
                (id_container.contig_to_vertex(c_id), c_or),
                (id_container.contig_to_vertex(d_id), d_or),
            ),
        )

    return mdcg, id_container
