# -*- coding=utf-8 -*-

"""Unit testing for assembly graph."""

# pylint: disable=compare-to-zero, missing-raises-doc
from pathlib import Path

from revsymg.graphs import RevSymGraph
from revsymg.index_lib import FORWARD_INT, REVERSE_INT, IndOrT

from khloraascaf.assembly_graph import (
    AssemblyGraph,
    OrCT,
    fmt_oriented_contig_paths_filename,
    fmt_region_paths_filename,
    read_oriented_contig_paths,
    read_region_paths,
    rev_oriented_contig,
    write_oriented_contig_paths,
    write_region_paths,
)


# ============================================================================ #
#                                   CONSTANTS                                  #
# ============================================================================ #
TEST_DIR: Path = Path(__file__).parent.absolute()

_TOY_DATADIR = TEST_DIR / 'data'

# ---------------------------------------------------------------------------- #
#                                    IR - SC                                   #
# ---------------------------------------------------------------------------- #
_IR_SC_DIR = _TOY_DATADIR / 'ir_sc'
_IR_SC_SOL_REGMAP = _IR_SC_DIR / 'map_of_regions_sol.tsv'
_IR_SC_SOL_REGCTG_F = _IR_SC_DIR / 'contigs_of_regions_sol_0.tsv'
_IR_SC_REG_PATHS = _IR_SC_DIR / 'region_paths.tsv'
_IR_SC_ORC_PATHS = _IR_SC_DIR / 'oriented_contig_paths.tsv'

# ---------------------------------------------------------------------------- #
#                                    DR - SC                                   #
# ---------------------------------------------------------------------------- #
_DR_SC_DIR = _TOY_DATADIR / 'dr_sc'
_DR_SC_SOL_REGMAP = _DR_SC_DIR / 'map_of_regions_sol.tsv'
_DR_SC_SOL_REGCTG = _DR_SC_DIR / 'contigs_of_regions_sol.tsv'
_DR_SC_REG_PATHS = _DR_SC_DIR / 'region_paths.tsv'
_DR_SC_ORC_PATHS = _DR_SC_DIR / 'oriented_contig_paths.tsv'


# ---------------------------------------------------------------------------- #
#                                      SC                                      #
# ---------------------------------------------------------------------------- #
_SC_DIR = _TOY_DATADIR / 'sc'
_SC_SOL_REGMAP = _SC_DIR / 'map_of_regions_sol.tsv'
_SC_SOL_REGCTG = _SC_DIR / 'contigs_of_regions_sol.tsv'


# ============================================================================ #
#                                TEST FUNCTIONS                                #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                               All_region_paths                               #
# ---------------------------------------------------------------------------- #
def test_all_region_paths_ir_sc():
    """Test all_region_paths method for IR-SC."""
    # TOTEST use fixture for assembly graph
    asm_graph = AssemblyGraph(
        _IR_SC_SOL_REGMAP,
        _IR_SC_SOL_REGCTG_F,
    )
    s_region_paths: set[tuple[IndOrT, ...]] = {
        (
            (0, FORWARD_INT),
            (1, FORWARD_INT),
            (2, FORWARD_INT),
            (1, REVERSE_INT),
        ),
        (
            (0, FORWARD_INT),
            (1, FORWARD_INT),
            (2, REVERSE_INT),
            (1, REVERSE_INT),
        ),
    }
    asm_graph_paths = tuple(asm_graph.all_region_paths())
    assert len(asm_graph_paths) == len(s_region_paths)
    assert set(asm_graph_paths) == s_region_paths


def test_all_region_paths_dr_sc():
    """Test all_region_paths method for DR-SC."""
    # TOTEST use fixture for assembly graph
    asm_graph = AssemblyGraph(
        _DR_SC_SOL_REGMAP,
        _DR_SC_SOL_REGCTG,
    )
    s_region_paths: set[tuple[IndOrT, ...]] = {
        (
            (0, FORWARD_INT),
            (1, FORWARD_INT),
            (2, FORWARD_INT),
            (1, FORWARD_INT),
        ),
    }
    asm_graph_paths = tuple(asm_graph.all_region_paths())
    assert len(asm_graph_paths) == len(s_region_paths)
    assert set(asm_graph_paths) == s_region_paths


# TOTEST test_all_regions_paths_sc
def test_all_region_paths_sc():
    """Test all_region_paths method for SC."""
    # TOTEST use fixture for assembly graph
    asm_graph = AssemblyGraph(
        _SC_SOL_REGMAP,
        _SC_SOL_REGCTG,
    )
    s_region_paths: set[tuple[IndOrT, ...]] = {
        (
            (0, FORWARD_INT),
        ),
    }
    asm_graph_paths = tuple(asm_graph.all_region_paths())
    assert len(asm_graph_paths) == len(s_region_paths)
    assert set(asm_graph_paths) == s_region_paths


# ---------------------------------------------------------------------------- #
#                           All_oriented_contig_paths                          #
# ---------------------------------------------------------------------------- #
def test_all_oriented_contig_paths_ir_sc():
    """Test all_oriented_contig_paths method for IR-SC."""
    # TOTEST use fixture for assembly graph
    asm_graph = AssemblyGraph(
        _IR_SC_SOL_REGMAP,
        _IR_SC_SOL_REGCTG_F,
    )
    s_orc_paths: set[tuple[OrCT, ...]] = {
        (
            ('C0', FORWARD_INT),
            ('C1', REVERSE_INT),
            ('C2', REVERSE_INT),
            ('C3', FORWARD_INT),
            ('C4', REVERSE_INT),
            ('C3', REVERSE_INT),
            ('C2', FORWARD_INT),
        ),
        (
            ('C0', FORWARD_INT),
            ('C1', REVERSE_INT),
            ('C2', REVERSE_INT),
            ('C3', FORWARD_INT),
            ('C4', FORWARD_INT),
            ('C3', REVERSE_INT),
            ('C2', FORWARD_INT),
        ),
    }
    asm_graph_paths = tuple(asm_graph.all_oriented_contig_paths())
    assert len(asm_graph_paths) == len(s_orc_paths)
    assert set(asm_graph_paths) == s_orc_paths


def test_all_oriented_contig_paths_dr_sc():
    """Test all_oriented_contig_paths method for DR-SC."""
    # TOTEST use fixture for assembly graph
    asm_graph = AssemblyGraph(
        _DR_SC_SOL_REGMAP,
        _DR_SC_SOL_REGCTG,
    )
    s_orc_paths: set[tuple[OrCT, ...]] = {
        (
            ('C0', REVERSE_INT),
            ('C1', FORWARD_INT),
            ('C2', REVERSE_INT),
            ('C3', FORWARD_INT),
            ('C4', REVERSE_INT),
            ('C2', REVERSE_INT),
            ('C3', FORWARD_INT),
        ),
    }
    asm_graph_paths = tuple(asm_graph.all_oriented_contig_paths())
    assert len(asm_graph_paths) == len(s_orc_paths)
    assert set(asm_graph_paths) == s_orc_paths


# ---------------------------------------------------------------------------- #
#                                    Revsymg                                   #
# ---------------------------------------------------------------------------- #
def test_getter_revsymg():
    """Test getter revsymg."""
    # TOTEST use fixture for assembly graph
    asm_graph = AssemblyGraph(
        _IR_SC_SOL_REGMAP,
        _IR_SC_SOL_REGCTG_F,
    )
    # TOTEST use fixtures and composition
    # TOTEST find a better assertion
    assert isinstance(asm_graph.revsymg(), RevSymGraph)


# ---------------------------------------------------------------------------- #
#                          Oriented_contigs_of_region                          #
# ---------------------------------------------------------------------------- #
def test_oriented_contigs_of_region():
    """Test oriented_contigs_of_region method."""
    # TOTEST use fixture for assembly graph
    asm_graph = AssemblyGraph(
        _IR_SC_SOL_REGMAP,
        _IR_SC_SOL_REGCTG_F,
    )
    # TOTEST use fixtures and composition
    assert list(asm_graph.oriented_contigs_of_region(0)) == [
        ('C0', FORWARD_INT),
        ('C1', REVERSE_INT),
    ]
    assert list(asm_graph.oriented_contigs_of_region(0, FORWARD_INT)) == [
        ('C0', FORWARD_INT),
        ('C1', REVERSE_INT),
    ]
    assert list(asm_graph.oriented_contigs_of_region(0, REVERSE_INT)) == [
        ('C1', FORWARD_INT),
        ('C0', REVERSE_INT),
    ]


# ---------------------------------------------------------------------------- #
#                              Rev_oriented_contig                             #
# ---------------------------------------------------------------------------- #
def test_rev_oriented_contig():
    """Test rev_oriented_contig function."""
    assert rev_oriented_contig(('0', FORWARD_INT)) == ('0', REVERSE_INT)
    assert rev_oriented_contig(('3', REVERSE_INT)) == ('3', FORWARD_INT)


# ---------------------------------------------------------------------------- #
#                              Write_region_paths                              #
# ---------------------------------------------------------------------------- #
def test_write_region_paths():
    """Test write_region_paths function."""
    asm_graph = AssemblyGraph(
        _IR_SC_SOL_REGMAP,
        _IR_SC_SOL_REGCTG_F,
    )
    region_paths_file = Path('tmp_region_paths.tsv')
    write_region_paths(asm_graph.all_region_paths(), region_paths_file)
    with open(region_paths_file, 'r', encoding='utf-8') as f_in:
        to_test_lines: set[tuple[str, ...]] = {
            tuple(line.split()) for line in f_in
        }
    with open(_IR_SC_REG_PATHS, 'r', encoding='utf-8') as f_in:
        sol_lines: set[tuple[str, ...]] = {
            tuple(line.split()) for line in f_in
        }
    assert to_test_lines == sol_lines
    region_paths_file.unlink()


# ---------------------------------------------------------------------------- #
#                               Read_region_paths                              #
# ---------------------------------------------------------------------------- #
def test_read_region_paths():
    """Test read_region_paths function."""
    region_paths = read_region_paths(_IR_SC_REG_PATHS)
    s_region_paths: set[tuple[IndOrT, ...]] = {
        (
            (0, FORWARD_INT),
            (1, FORWARD_INT),
            (2, FORWARD_INT),
            (1, REVERSE_INT),
        ),
        (
            (0, FORWARD_INT),
            (1, FORWARD_INT),
            (2, REVERSE_INT),
            (1, REVERSE_INT),
        ),
    }
    for region_path in region_paths:
        assert tuple(region_path) in s_region_paths


# ---------------------------------------------------------------------------- #
#                           Fmt_region_paths_filename                          #
# ---------------------------------------------------------------------------- #
def test_fmt_region_paths_file():
    """Test fmt_region_paths_filename."""
    assert fmt_region_paths_filename('jaaj', ('ir', 'sc')) == (
        'region_paths_jaaj_ir_sc.tsv'
    )


# ---------------------------------------------------------------------------- #
#                          Write_oriented_contig_paths                         #
# ---------------------------------------------------------------------------- #
def test_write_oriented_contig_paths():
    """Test write_oriented_contig_paths function."""
    asm_graph = AssemblyGraph(
        _IR_SC_SOL_REGMAP,
        _IR_SC_SOL_REGCTG_F,
    )
    oriented_contig_paths_file = Path('tmp_oriented_contig_paths.tsv')
    write_oriented_contig_paths(
        asm_graph.all_oriented_contig_paths(),
        oriented_contig_paths_file)
    with open(oriented_contig_paths_file, 'r', encoding='utf-8') as f_in:
        to_test_lines: set[tuple[str, ...]] = {
            tuple(line.split()) for line in f_in
        }
    with open(_IR_SC_ORC_PATHS, 'r', encoding='utf-8') as f_in:
        sol_lines: set[tuple[str, ...]] = {
            tuple(line.split()) for line in f_in
        }
    assert to_test_lines == sol_lines
    oriented_contig_paths_file.unlink()


# ---------------------------------------------------------------------------- #
#                          Read_oriented_contig_paths                          #
# ---------------------------------------------------------------------------- #
def test_read_oriented_contig_paths():
    """Test read_oriented_contig_paths function."""
    oriented_contig_paths = read_oriented_contig_paths(_IR_SC_ORC_PATHS)
    s_oriented_contig_paths: set[tuple[OrCT, ...]] = {
        (
            ('C0', FORWARD_INT),
            ('C1', REVERSE_INT),
            ('C2', REVERSE_INT),
            ('C3', FORWARD_INT),
            ('C4', REVERSE_INT),
            ('C3', REVERSE_INT),
            ('C2', FORWARD_INT),
        ),
        (
            ('C0', FORWARD_INT),
            ('C1', REVERSE_INT),
            ('C2', REVERSE_INT),
            ('C3', FORWARD_INT),
            ('C4', FORWARD_INT),
            ('C3', REVERSE_INT),
            ('C2', FORWARD_INT),
        ),
    }
    for oriented_contig_path in oriented_contig_paths:
        assert tuple(oriented_contig_path) in s_oriented_contig_paths


# ---------------------------------------------------------------------------- #
#                      Fmt_oriented_contig_paths_filename                      #
# ---------------------------------------------------------------------------- #
def test_fmt_oriented_contig_paths_file():
    """Test fmt_oriented_contig_paths_filename."""
    assert fmt_oriented_contig_paths_filename('jaaj', ('ir', 'sc')) == (
        'oriented_contig_paths_jaaj_ir_sc.tsv'
    )
