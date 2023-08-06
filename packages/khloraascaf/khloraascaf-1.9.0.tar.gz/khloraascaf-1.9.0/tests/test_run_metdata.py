# -*- coding=utf-8 -*-

"""Unit testing for run metadata."""

# pylint: disable=missing-yield-doc,redefined-outer-name,
# flake8: noqa D103

from collections.abc import Iterator
from pathlib import Path

import pytest
import yaml  # type: ignore

from khloraascaf.exceptions import NoSolution
from khloraascaf.inputs import (
    INSTANCE_NAME_DEF,
    MULT_UPB_DEF,
    PRESSCORE_UPB_DEF,
    SOLVER_CBC,
)
from khloraascaf.lib import IR_REGION_ID, SC_REGION_ID
from khloraascaf.run_metadata import (
    IOConfig,
    MetadataAllDebugs,
    MetadataAllSolutions,
    MetadataDebug,
    MetadataSolution,
    str_to_vertex,
    vertex_to_str,
)


# ============================================================================ #
#                                   CONSTANTS                                  #
# ============================================================================ #
TEST_DIR: Path = Path(__file__).parent.absolute()

_TOY_DATADIR = TEST_DIR / 'data'

# ---------------------------------------------------------------------------- #
#                                    IR - SC                                   #
# ---------------------------------------------------------------------------- #
# REFACTOR logic behin tests: do class
_IR_SC_DIR = _TOY_DATADIR / 'ir_sc'
_IR_SC_CONTIG_ATTRS = _IR_SC_DIR / 'contig_attrs.tsv'
_IR_SC_CONTIG_LINKS = _IR_SC_DIR / 'contig_links.tsv'
_IR_SC_CONTIG_STARTER = 'C0'

#
# YAML files
#
_IR_SC_IOCONFIG_YAML = _IR_SC_DIR / 'io_config.yaml'
_IR_SC_SOLUTION_YAML = _IR_SC_DIR / 'solution.yaml'
_IR_SC_SOLUTIONS_YAML = _IR_SC_DIR / 'solutions.yaml'
_IR_SC_DEBUG_YAML = _IR_SC_DIR / 'debug.yaml'
_IR_SC_DEBUGS_YAML = _IR_SC_DIR / 'debugs.yaml'

# REFACTOR uniformise the constants with toy example
_IR_SC_MAP = _IR_SC_DIR / 'map_of_regions_khloraascaf_ir_sc.tsv'
_IR_SC_CTGREG = _IR_SC_DIR / 'contigs_of_regions_khloraascaf_ir_sc.tsv'
_IR_SC_VERTICESREG = _IR_SC_DIR / 'vertices_of_regions_khloraascaf_ir.tsv'
_IR_SC_MAP_DEBUG = _IR_SC_DIR / 'map_of_regions_khloraascaf_ir.tsv'
_IR_SC_REPFRAG = _IR_SC_DIR / 'repfrag_khloraascaf_ir.tsv'


# ============================================================================ #
#                              IOCONFIG CLASS TEST                             #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                                    Fixture                                   #
# ---------------------------------------------------------------------------- #
@pytest.fixture
def io_cfg_ir_sc() -> Iterator[IOConfig]:
    """Fixture IOConfig for ir-sc."""
    yield IOConfig.from_run_directory(_IR_SC_DIR)


# ---------------------------------------------------------------------------- #
#                                 Test Methods                                 #
# ---------------------------------------------------------------------------- #
def test_iocfg_from_run_dir(io_cfg_ir_sc: IOConfig):
    assert io_cfg_ir_sc


def test_iocfg_config_directory(io_cfg_ir_sc: IOConfig):
    assert io_cfg_ir_sc.io_config_directory() == _IR_SC_DIR


def test_iocfg_contig_attrs(io_cfg_ir_sc: IOConfig):
    assert (
        io_cfg_ir_sc.contig_attrs()
        == _IR_SC_CONTIG_ATTRS.relative_to(_IR_SC_DIR)
    )


def test_iocfg_contig_links(io_cfg_ir_sc: IOConfig):
    assert (
        io_cfg_ir_sc.contig_links()
        == _IR_SC_CONTIG_LINKS.relative_to(_IR_SC_DIR)
    )


def test_iocfg_contig_starter(io_cfg_ir_sc: IOConfig):
    assert io_cfg_ir_sc.contig_starter() == _IR_SC_CONTIG_STARTER


def test_iocfg_mult_upb(io_cfg_ir_sc: IOConfig):
    assert io_cfg_ir_sc.mult_upb() == MULT_UPB_DEF


def test_iocfg_presscore_upb(io_cfg_ir_sc: IOConfig):
    assert io_cfg_ir_sc.presscore_upb() == PRESSCORE_UPB_DEF


def test_iocfg_solver(io_cfg_ir_sc: IOConfig):
    assert io_cfg_ir_sc.solver() == SOLVER_CBC


def test_iocfg_outdir(io_cfg_ir_sc: IOConfig):
    assert (
        io_cfg_ir_sc.outdir()
        == (_IR_SC_DIR / 'tmp').relative_to(_IR_SC_DIR)
    )


def test_iocfg_instance_name(io_cfg_ir_sc: IOConfig):
    assert io_cfg_ir_sc.instance_name() == INSTANCE_NAME_DEF


def test_iocfg_debug(io_cfg_ir_sc: IOConfig):
    assert io_cfg_ir_sc.debug()


def test_iocfg_write_yaml(io_cfg_ir_sc: IOConfig):
    true_io_cfg_path = _IR_SC_DIR / 'true_io_config.yaml'
    _IR_SC_IOCONFIG_YAML.rename(true_io_cfg_path)
    io_cfg_ir_sc.write_yaml()
    assert _IR_SC_IOCONFIG_YAML.exists()
    with (open(true_io_cfg_path, 'r', encoding='utf-8') as t_in,
            open(_IR_SC_IOCONFIG_YAML, 'r', encoding='utf-8') as f_in):
        assert yaml.load(t_in, yaml.Loader) == yaml.load(f_in, yaml.Loader)
    _IR_SC_IOCONFIG_YAML.unlink()
    true_io_cfg_path.rename(_IR_SC_IOCONFIG_YAML)


def test_iocfg_yaml_path(io_cfg_ir_sc: IOConfig):
    assert io_cfg_ir_sc.yaml_path() == _IR_SC_IOCONFIG_YAML


# ============================================================================ #
#                            METADATASOLUTION CLASS                            #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                                    Fixture                                   #
# ---------------------------------------------------------------------------- #
@pytest.fixture
def sol_meta_ir_sc() -> Iterator[MetadataSolution]:
    """Fixture MetadataSolution for ir-sc."""
    yield MetadataSolution.from_run_directory(_IR_SC_DIR)


# ---------------------------------------------------------------------------- #
#                                 Test Methods                                 #
# ---------------------------------------------------------------------------- #
def test_sol_meta_there_is_a_sol():
    assert MetadataSolution.there_is_a_solution(_IR_SC_DIR)


def test_sol_meta_from_run_dir(sol_meta_ir_sc: MetadataSolution):
    assert sol_meta_ir_sc


def test_sol_meta_from_run_dir_fail():
    try:
        assert MetadataSolution.from_run_directory(Path('. /'))
    except NoSolution:
        assert True
    else:
        raise AssertionError


def test_sol_meta_solution_directory(sol_meta_ir_sc: MetadataSolution):
    assert sol_meta_ir_sc.solution_directory() == _IR_SC_DIR


def test_sol_meta_ilp_combination(sol_meta_ir_sc: MetadataSolution):
    assert sol_meta_ir_sc.ilp_combination() == [IR_REGION_ID, SC_REGION_ID]


def test_sol_meta_contigs_of_regions(sol_meta_ir_sc: MetadataSolution):
    assert sol_meta_ir_sc.contigs_of_regions() == Path(_IR_SC_CTGREG.name)


def test_sol_meta_map_of_regions(sol_meta_ir_sc: MetadataSolution):
    assert sol_meta_ir_sc.map_of_regions() == Path(_IR_SC_MAP.name)


def test_sol_meta_write_yaml(sol_meta_ir_sc: MetadataSolution):
    true_sol_meta_path = _IR_SC_DIR / 'true_solution.yaml'
    _IR_SC_SOLUTION_YAML.rename(true_sol_meta_path)
    sol_meta_ir_sc.write_yaml()
    assert _IR_SC_SOLUTION_YAML.exists()
    with (open(true_sol_meta_path, 'r', encoding='utf-8') as t_in,
            open(_IR_SC_SOLUTION_YAML, 'r', encoding='utf-8') as f_in):
        assert yaml.load(t_in, yaml.Loader) == yaml.load(f_in, yaml.Loader)
    _IR_SC_SOLUTION_YAML.unlink()
    true_sol_meta_path.rename(_IR_SC_SOLUTION_YAML)


def test_sol_meta_yaml_path(sol_meta_ir_sc: MetadataSolution):
    assert sol_meta_ir_sc.yaml_path() == _IR_SC_SOLUTION_YAML


# ============================================================================ #
#                          METADATAALLSOLUTIONS CLASS                          #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                                    Fixture                                   #
# ---------------------------------------------------------------------------- #
@pytest.fixture
def allsol_meta_ir_sc() -> Iterator[MetadataAllSolutions]:
    """Fixture MetadataAllSolutions for ir-sc."""
    yield MetadataAllSolutions.from_run_directory(_IR_SC_DIR)


# ---------------------------------------------------------------------------- #
#                                 Test Methods                                 #
# ---------------------------------------------------------------------------- #
def test_allsol_meta_there_is_a_sol():
    assert MetadataAllSolutions.there_is_a_solution(_IR_SC_DIR)


def test_allsol_meta_from_run_dir(allsol_meta_ir_sc: MetadataAllSolutions):
    assert allsol_meta_ir_sc


def test_sol_meta_from_run_dir_empty():
    nosol_meta = MetadataAllSolutions.from_run_directory(Path('. /'))
    assert not nosol_meta


def test_allsol_meta_solutions_directory(
        allsol_meta_ir_sc: MetadataAllSolutions):
    assert allsol_meta_ir_sc.solutions_directory() == _IR_SC_DIR


def test_allsol_meta_iter(allsol_meta_ir_sc: MetadataAllSolutions):
    assert sum(1 for _ in allsol_meta_ir_sc) == 1


def test_allsol_meta_len(allsol_meta_ir_sc: MetadataAllSolutions):
    assert len(allsol_meta_ir_sc) == 1


def test_allsol_meta_write_yaml(allsol_meta_ir_sc: MetadataAllSolutions):
    true_allsol_meta_path = _IR_SC_DIR / 'true_solutions.yaml'
    _IR_SC_SOLUTIONS_YAML.rename(true_allsol_meta_path)
    allsol_meta_ir_sc.write_yaml()
    assert _IR_SC_SOLUTIONS_YAML.exists()
    with (open(true_allsol_meta_path, 'r', encoding='utf-8') as t_in,
            open(_IR_SC_SOLUTIONS_YAML, 'r', encoding='utf-8') as f_in):
        assert yaml.load(t_in, yaml.Loader) == yaml.load(f_in, yaml.Loader)
    _IR_SC_SOLUTIONS_YAML.unlink()
    true_allsol_meta_path.rename(_IR_SC_SOLUTIONS_YAML)


def test_allsol_meta_yaml_path(allsol_meta_ir_sc: MetadataAllSolutions):
    assert allsol_meta_ir_sc.yaml_path() == _IR_SC_SOLUTIONS_YAML


# ============================================================================ #
#                              METADATADEBUG CLASS                             #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                                    Fixture                                   #
# ---------------------------------------------------------------------------- #
@pytest.fixture
def debug_meta_ir_sc() -> Iterator[MetadataDebug]:
    """Fixture MetadataDebug for ir-sc."""
    yield MetadataDebug.from_run_directory(_IR_SC_DIR)


# ---------------------------------------------------------------------------- #
#                                 Test Methods                                 #
# ---------------------------------------------------------------------------- #
def test_debug_meta_from_run_dir(debug_meta_ir_sc: MetadataDebug):
    assert debug_meta_ir_sc


def test_debug_meta_run_directory(debug_meta_ir_sc: MetadataDebug):
    assert debug_meta_ir_sc.run_directory() == _IR_SC_DIR


def test_debug_meta_ilp_combination(debug_meta_ir_sc: MetadataDebug):
    assert debug_meta_ir_sc.ilp_combination() == [IR_REGION_ID]


def test_debug_meta_starter_vertex(debug_meta_ir_sc: MetadataDebug):
    assert debug_meta_ir_sc.starter_vertex() == (0, 0, 0)


def test_debug_meta_ilp_status(debug_meta_ir_sc: MetadataDebug):
    assert debug_meta_ir_sc.ilp_status() == 'Optimal'


def test_debug_meta_opt_value(debug_meta_ir_sc: MetadataDebug):
    assert debug_meta_ir_sc.opt_value() == 3.0


def test_debug_meta_vertices_of_regions(debug_meta_ir_sc: MetadataDebug):
    assert debug_meta_ir_sc.vertices_of_regions() == Path(
        _IR_SC_VERTICESREG.name)


def test_debug_meta_map_of_regions(debug_meta_ir_sc: MetadataDebug):
    assert debug_meta_ir_sc.map_of_regions() == Path(_IR_SC_MAP_DEBUG.name)


def test_debug_meta_repeat_fragments(debug_meta_ir_sc: MetadataDebug):
    assert debug_meta_ir_sc.repeat_fragments() == Path(_IR_SC_REPFRAG.name)


def test_debug_meta_write_yaml(debug_meta_ir_sc: MetadataDebug):
    true_debug_meta_path = _IR_SC_DIR / 'true_debug.yaml'
    _IR_SC_DEBUG_YAML.rename(true_debug_meta_path)
    debug_meta_ir_sc.write_yaml()
    assert _IR_SC_DEBUG_YAML.exists()
    with (open(true_debug_meta_path, 'r', encoding='utf-8') as t_in,
            open(_IR_SC_DEBUG_YAML, 'r', encoding='utf-8') as f_in):
        assert yaml.load(t_in, yaml.Loader) == yaml.load(f_in, yaml.Loader)
    _IR_SC_DEBUG_YAML.unlink()
    true_debug_meta_path.rename(_IR_SC_DEBUG_YAML)


def test_debug_meta_yaml_path(debug_meta_ir_sc: MetadataDebug):
    assert debug_meta_ir_sc.yaml_path() == _IR_SC_DEBUG_YAML


# ============================================================================ #
#                               METADATAALLDEBUGS                              #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                                    Fixture                                   #
# ---------------------------------------------------------------------------- #
@pytest.fixture
def alldebugs_meta_ir_sc() -> Iterator[MetadataAllDebugs]:
    """Fixture MetadataAllDebugs for ir-sc."""
    yield MetadataAllDebugs.from_run_directory(_IR_SC_DIR)


# ---------------------------------------------------------------------------- #
#                                 Test Methods                                 #
# ---------------------------------------------------------------------------- #
def test_alldebugs_meta_from_run_dir(alldebugs_meta_ir_sc: MetadataAllDebugs):
    assert alldebugs_meta_ir_sc


def test_alldebugs_meta_run_dir(alldebugs_meta_ir_sc: MetadataAllDebugs):
    assert alldebugs_meta_ir_sc.runs_directory() == _IR_SC_DIR


def test_alldebugs_meta_iter(alldebugs_meta_ir_sc: MetadataAllDebugs):
    assert sum(1 for _ in alldebugs_meta_ir_sc) == 4


def test_alldebugs_meta_len(alldebugs_meta_ir_sc: MetadataAllDebugs):
    assert len(alldebugs_meta_ir_sc) == 4


def test_alldebugs_meta_write_yaml(alldebugs_meta_ir_sc: MetadataAllDebugs):
    true_alldebugs_meta_path = _IR_SC_DIR / 'true_debugs.yaml'
    _IR_SC_DEBUGS_YAML.rename(true_alldebugs_meta_path)
    alldebugs_meta_ir_sc.write_yaml()
    assert _IR_SC_DEBUGS_YAML.exists()
    with (open(true_alldebugs_meta_path, 'r', encoding='utf-8') as t_in,
            open(_IR_SC_DEBUGS_YAML, 'r', encoding='utf-8') as f_in):
        assert yaml.load(t_in, yaml.Loader) == yaml.load(f_in, yaml.Loader)
    _IR_SC_DEBUGS_YAML.unlink()
    true_alldebugs_meta_path.rename(_IR_SC_DEBUGS_YAML)


def test_alldebugs_meta_yaml_path(alldebugs_meta_ir_sc: MetadataAllDebugs):
    assert alldebugs_meta_ir_sc.yaml_path() == _IR_SC_DEBUGS_YAML


# ============================================================================ #
#                                FUNCTIONS TESTS                               #
# ============================================================================ #
def test_vertex_to_str():
    assert vertex_to_str((1, 0, 4)) == '1\t+\t4'
    assert vertex_to_str((8, 1, 0)) == '8\t-\t0'


def test_str_to_vertex():
    assert str_to_vertex('1\t+\t4') == (1, 0, 4)
    assert str_to_vertex('8\t-\t0') == (8, 1, 0)
