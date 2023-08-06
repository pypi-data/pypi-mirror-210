# -*- coding=utf-8 -*-

"""NetworkX and GraphML utilities."""

from __future__ import annotations

from collections.abc import Iterable

from khloraascaf import DR_REGION_ID, IR_REGION_ID, MetadataDebug
from khloraascaf.ilp.dirf_sets import DirFT, dirf, dirf_builder, dirf_other
from khloraascaf.ilp.invf_sets import InvFT, invf, invf_builder, invf_other
from khloraascaf.multiplied_doubled_contig_graph import (
    CIND_IND,
    COCC_IND,
    COR_IND,
    CTG_ID_ATTR,
    MULT_ATTR,
    PRESSCORE_ATTR,
    MDCGraph,
    MDCGraphIDContainer,
    OccOrCT,
)
from khloraascaf.outputs import ORIENT_INT_STR, read_map_of_regions
from khloraascaf.utils_debug import (
    DIRF_CODE,
    INVF_CODE,
    read_found_repeated_fragments,
    read_vertices_of_regions,
)
from networkx import DiGraph
from revsymg.index_lib import FORWARD_INT, REVERSE_INT, IndexT


# DOCU docstring constants
# DOCU new functions
# ============================================================================ #
#                                   CONSTANTS                                  #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                              Graph Relation Type                             #
# ---------------------------------------------------------------------------- #
RELATION_ATTR = 'relation'
"""Relation attribute name on edges.

Its value can be :data:`~khloraascaf_utils.to_networkx.EDGE_ATTRVAL`,
:data:`~khloraascaf_utils.to_networkx.INVF_ATTRVAL`
or :data:`~khloraascaf_utils.to_networkx.DIRF_ATTRVAL`.
"""

EDGE_ATTRVAL = 'edge'
"""Property that assumes the edge is an edge in MDCG."""

INVF_ATTRVAL = 'inverted_fragment'
"""Property that assumes the edge is an inverted fragment in MDCG."""

DIRF_ATTRVAL = 'direct_fragment'
"""Property that assumes the edge is a direct fragment in MDCG."""

# ---------------------------------------------------------------------------- #
#                                   Solution                                   #
# ---------------------------------------------------------------------------- #
SOLUTION_PATH_PREFIX_ATTR = 'solution_path'
"""Prefix to write the solution path on the edges."""

SOLUTION_DIRF_PREFIX_ATTR = f'solution_{DIRF_CODE}'
"""Prefix to write the solution direct fragments."""

SOLUTION_INVF_PREFIX_ATTR = f'solution_{INVF_CODE}'
"""Prefix to write the solution inverted fragments."""

SOLUTION_REGION_IND = 'solution_region'
"""Prefix for the vertices' region index attribute."""


# ---------------------------------------------------------------------------- #
#                                  File Output                                 #
# ---------------------------------------------------------------------------- #
GRAPHML_EXT = 'graphml'
"""GraphML file extension."""


# ============================================================================ #
#                                   FUNCTIONS                                  #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                             Initialise NxDigraph                             #
# ---------------------------------------------------------------------------- #
def mdcg_to_nxdigraph(mdcg: MDCGraph,
                      id_container: MDCGraphIDContainer) -> DiGraph:
    """Format mdcg graph to a networkx digraph.

    Parameters
    ----------
    mdcg : MDCGraph
        Multiplied doubled contig graph
    id_container : MDCGraphIDContainer
        Identifiers container

    Returns
    -------
    DiGraph
        NetworkX graph
    """
    vertices = mdcg.vertices()

    nxgraph = DiGraph()
    # ------------------------------------------------------------------------ #
    # Add OccOrCT
    # ------------------------------------------------------------------------ #
    # All but start and terminal
    for v_ind, v_or, v_occ in mdcg.multiplied_vertices():
        nxgraph.add_node(
            format_occorc_to_nxnode((v_ind, v_or, v_occ)),
            ** {
                CTG_ID_ATTR: id_container.vertex_to_contig(v_ind),
                MULT_ATTR: vertices.attr(v_ind, MULT_ATTR),
                PRESSCORE_ATTR: vertices.attr(v_ind, PRESSCORE_ATTR),
            },
        )
    # ------------------------------------------------------------------------ #
    # Add EOccOrCT
    # ------------------------------------------------------------------------ #
    for (u_ind, u_or, u_occ), (v_ind, v_or, v_occ) in mdcg.multiplied_edges():
        nxgraph.add_edge(
            format_occorc_to_nxnode((u_ind, u_or, u_occ)),
            format_occorc_to_nxnode((v_ind, v_or, v_occ)),
            **{RELATION_ATTR: EDGE_ATTRVAL},
        )
    # ------------------------------------------------------------------------ #
    # Add inverted fragments
    # ------------------------------------------------------------------------ #
    for i, j in invf(mdcg):
        nxgraph.add_edge(
            format_occorc_to_nxnode(i),
            format_occorc_to_nxnode(j),
            ** {RELATION_ATTR: INVF_ATTRVAL},
        )
    # ------------------------------------------------------------------------ #
    # Add direct fragments
    # ------------------------------------------------------------------------ #
    for i, j in dirf(mdcg):
        nxgraph.add_edge(
            format_occorc_to_nxnode(i),
            format_occorc_to_nxnode(j),
            ** {RELATION_ATTR: DIRF_ATTRVAL},
        )
    return nxgraph


def format_occorc_to_nxnode(occorc: OccOrCT) -> str:
    """Format to a string a multiplied oriented contig.

    Parameters
    ----------
    occorc : OccOrCT
        Multiplied oriented contig

    Returns
    -------
    str
        NetworkX digraph node's identifier
    """
    return (
        f'{occorc[CIND_IND]}'
        f'{ORIENT_INT_STR[occorc[COR_IND]]}'
        f'{occorc[COCC_IND]}'
    )


# ---------------------------------------------------------------------------- #
#                         Add Vertices Of Regions Paths                        #
# ---------------------------------------------------------------------------- #
def add_result_in_nxdigraph_from_debug(nxgraph: DiGraph,
                                       debug_metadata: MetadataDebug):
    """Add the solution in the nx DiGraph.

    Parameters
    ----------
    nxgraph : DiGraph
        NetworkX DiGraph
    debug_metadata: MetadataDebug
        Debug metadata

    Notes
    -----
    The repeated fragments added into the graph are these of the last
    scaffolding, e.g. for the ilp combination ir-dr,
    the repeated fragments of dr are added
    while for ir-dr-sc no repeated fragments are added.
    """
    attribute_suffix = '-'.join(debug_metadata.ilp_combination())
    # ------------------------------------------------------------------------ #
    # Record vertices and oriented regions path
    # ------------------------------------------------------------------------ #
    vertices_regions: tuple[tuple[OccOrCT, ...], ...] = tuple(
        read_vertices_of_regions(debug_metadata.vertices_of_regions()),
    )
    first_region_discovered: list[bool] = [False] * len(vertices_regions)

    # ------------------------------------------------------------------------ #
    # Add the solutions path and repeated fragments
    # ------------------------------------------------------------------------ #
    vertex_path: list[OccOrCT] = []
    for reg_ind, reg_or in read_map_of_regions(debug_metadata.map_of_regions()):

        previous_end = len(vertex_path) - 1
        if reg_or == FORWARD_INT:
            if first_region_discovered[reg_ind]:
                vertex_path.extend(
                    dirf_other(v) for v in vertices_regions[reg_ind]
                )
            else:
                vertex_path.extend(vertices_regions[reg_ind])
        elif reg_or == REVERSE_INT:
            # Special case: if reverse, then it is the second IR
            vertex_path.extend(
                invf_other(v) for v in reversed(vertices_regions[reg_ind])
            )

        add_solution_vertices_region_index(
            nxgraph, vertex_path[previous_end + 1:], reg_ind, attribute_suffix)
        first_region_discovered[reg_ind] = True

    vertex_path.append(vertex_path[0])
    add_solution_path_in_nxdigraph(nxgraph, vertex_path, attribute_suffix)

    # ------------------------------------------------------------------------ #
    # Add repeated fragments
    # ------------------------------------------------------------------------ #
    if debug_metadata.ilp_combination()[-1] == DR_REGION_ID:
        add_solution_dirf_in_nxdigraph(
            nxgraph,
            (
                dirf_builder(v)[0]
                for _, v in read_found_repeated_fragments(
                    debug_metadata.repeat_fragments())
            ),
            attribute_suffix,
        )
    elif debug_metadata.ilp_combination()[-1] == IR_REGION_ID:
        add_solution_invf_in_nxdigraph(
            nxgraph,
            (
                invf_builder(v)[0]
                for _, v in read_found_repeated_fragments(
                    debug_metadata.repeat_fragments())
            ),
            attribute_suffix,
        )


# ---------------------------------------------------------------------------- #
#                           Add Vertex Path Solution                           #
# ---------------------------------------------------------------------------- #
def add_solution_path_in_nxdigraph(nxgraph: DiGraph,
                                   vertex_path: Iterable[OccOrCT],
                                   attribute_suffix: str):
    """Add the solutions' path to the networkx graph.

    Parameters
    ----------
    nxgraph : DiGraph
        NetworkX mdcg graph
    vertex_path : iterable of OccOrCT
        Vertex path
    attribute_suffix : str
        Suffix for the attribute name
    """
    vertex_path_iter = iter(vertex_path)
    u = next(vertex_path_iter)
    for v in vertex_path_iter:
        nxgraph.edges[
            format_occorc_to_nxnode(u),
            format_occorc_to_nxnode(v),
        ][solution_path_attr(attribute_suffix)] = True
        u = v


def solution_path_attr(attribute_suffix: str) -> str:
    """Format the attribute name for the solution's path.

    Parameters
    ----------
    attribute_suffix : str
        Suffix for the attribute name

    Returns
    -------
    str
        Formatted string attribute name
    """
    return (
        SOLUTION_PATH_PREFIX_ATTR
        + f'_{attribute_suffix}' if attribute_suffix else ''
    )


# ---------------------------------------------------------------------------- #
#                               Add Vertex Region                              #
# ---------------------------------------------------------------------------- #
def add_solution_vertices_region_index(nxgraph: DiGraph,
                                       vertex_path: Iterable[OccOrCT],
                                       region_index: IndexT,
                                       attribute_suffix: str):
    """Add for each vertex its region index in the networkx graph.

    Parameters
    ----------
    nxgraph : DiGraph
        NetworkX mdcg graph
    vertex_path : iterable of OccOrCT
        Solution's positions
    region_index : IndexT
        Region index of the vertices in the path
    attribute_suffix : str
        Suffix for the attribute name
    """
    for v in vertex_path:
        nxgraph.nodes[
            format_occorc_to_nxnode(v)
        ][solution_region_index_attr(attribute_suffix)] = region_index


def solution_region_index_attr(attribute_suffix: str) -> str:
    """Format the attribute name for the solution's region index.

    Parameters
    ----------
    attribute_suffix : str
        Suffix for the attribute name

    Returns
    -------
    str
        Formatted string attribute name
    """
    return (
        SOLUTION_REGION_IND
        + f'_{attribute_suffix}' if attribute_suffix else ''
    )


# ---------------------------------------------------------------------------- #
#                               Add InvF Solution                              #
# ---------------------------------------------------------------------------- #
def add_solution_invf_in_nxdigraph(nxgraph: DiGraph,
                                   sol_invf: Iterable[InvFT],
                                   attribute_suffix: str):
    """Add the solutions' inverted fragments to the networkx graph.

    Parameters
    ----------
    nxgraph : DiGraph
        NetworkX mdcg graph
    sol_invf : iterable of InvFT
        Solution's inverted fragments list
    attribute_suffix : str
        Suffix for the attribute name
    """
    for u, v in sol_invf:
        nxgraph.edges[
            format_occorc_to_nxnode(u),
            format_occorc_to_nxnode(v),
        ][solution_invf_attr(attribute_suffix)] = True


def solution_invf_attr(attribute_suffix: str) -> str:
    """Format the attribute name for the solution's inverted fragments.

    Parameters
    ----------
    attribute_suffix : str
        Suffix for the attribute name

    Returns
    -------
    str
        Formatted string attribute name
    """
    return (
        SOLUTION_INVF_PREFIX_ATTR
        + f'_{attribute_suffix}' if attribute_suffix else ''
    )


# ---------------------------------------------------------------------------- #
#                               Add DirF Solution                              #
# ---------------------------------------------------------------------------- #
def add_solution_dirf_in_nxdigraph(nxgraph: DiGraph,
                                   sol_dirf: Iterable[DirFT],
                                   attribute_suffix: str):
    """Add the solutions' direct fragments to the networkx graph.

    Parameters
    ----------
    nxgraph : DiGraph
        NetworkX mdcg graph
    sol_dirf : iterable of DirFT
        Solution's direct fragments list
    attribute_suffix : str
        Suffix for the attribute name
    """
    for u, v in sol_dirf:
        nxgraph.edges[
            format_occorc_to_nxnode(u),
            format_occorc_to_nxnode(v),
        ][solution_dirf_attr(attribute_suffix)] = True


def solution_dirf_attr(attribute_suffix: str) -> str:
    """Format the attribute name for the solution's direct fragments.

    Parameters
    ----------
    attribute_suffix : str
        Suffix for the attribute name

    Returns
    -------
    str
        Formatted string attribute name
    """
    return (
        SOLUTION_DIRF_PREFIX_ATTR
        + f'_{attribute_suffix}' if attribute_suffix else ''
    )
