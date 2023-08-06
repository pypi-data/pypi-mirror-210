# -*- coding=utf-8 -*-

"""Unit testing for assembly graph."""

# pylint: disable=compare-to-zero, missing-raises-doc

from pathlib import Path

from pulp import LpStatus, LpStatusInfeasible

from khloraascaf.exceptions import (
    CombineScaffoldingError,
    NoSolution,
    NotACircuit,
    RepeatScaffoldingError,
    ScaffoldingError,
    SingleCopyScaffoldingError,
    UnfeasibleDR,
    UnfeasibleIR,
    UnfeasibleSC,
    WrongRegionID,
    WrongSolverName,
)
from khloraascaf.lib import IR_REGION_ID, SC_REGION_ID


# ============================================================================ #
#                                TEST FUNCTIONS                                #
# ============================================================================ #
def test_scaffolding_error():
    """Test ScaffoldingError exception."""
    outdir_gen = Path('./jaaj')
    exc = ScaffoldingError(outdir_gen)
    assert exc.outdir_gen() == outdir_gen
    assert str(exc) == (
        'Scaffolding fails\n'
        '\tSee output directory: jaaj'
    )


def test_repeat_scaffolding_error():
    """Test RepeatScaffoldingError exception."""
    exc = RepeatScaffoldingError()
    assert str(exc) == 'Repeat scaffolding has failed'


def test_singlecopy_scaffolding_error():
    """Test SingleCopyScaffoldingError exception."""
    exc = SingleCopyScaffoldingError()
    assert str(exc) == 'Single copy scaffolding has failed'


def test_combine_scaffolding_error():
    """Test CombineScaffoldingError exception."""
    exc = CombineScaffoldingError()
    assert str(exc) == 'The scaffolding combination has failed'


def test_wrong_region_code():
    """Test WrongRegionID exception."""
    exc = WrongRegionID(IR_REGION_ID)
    assert exc.region_id() == IR_REGION_ID
    assert str(exc) == "The region identifier 'ir' is not correct"


def test_wrong_solver_name():
    """Test WrongSolverName exception."""
    wrong_solver_name = 'un_oracle_ma_dit'
    exc = WrongSolverName(wrong_solver_name)
    assert exc.solver() == wrong_solver_name
    assert str(exc) == 'The solver name un_oracle_ma_dit is not correct'


def test_unfeasible_ir():
    """Test UnfeasibleIR exception."""
    bad_status = LpStatus[LpStatusInfeasible]
    ilp_combi = (IR_REGION_ID, SC_REGION_ID)
    exc = UnfeasibleIR(bad_status, ilp_combi)
    assert exc.status() == bad_status
    assert exc.ilp_combi() == ilp_combi
    assert str(exc) == (
        'The Find the best inverted repeats problem is unfeasible:\n'
        '\t* ILP codes: ir-sc\n'
        '\t* Status: Infeasible'
    )


def test_unfeasible_dr():
    """Test UnfeasibleDR exception."""
    bad_status = LpStatus[LpStatusInfeasible]
    ilp_combi = (IR_REGION_ID, SC_REGION_ID)
    exc = UnfeasibleDR(bad_status, ilp_combi)
    assert exc.status() == bad_status
    assert exc.ilp_combi() == ilp_combi
    assert str(exc) == (
        'The Find the best direct repeats problem is unfeasible:\n'
        '\t* ILP codes: ir-sc\n'
        '\t* Status: Infeasible'
    )


def test_unfeasible_sc():
    """Test UnfeasibleSC exception."""
    bad_status = LpStatus[LpStatusInfeasible]
    ilp_combi = (IR_REGION_ID, SC_REGION_ID)
    exc = UnfeasibleSC(bad_status, ilp_combi)
    assert exc.status() == bad_status
    assert exc.ilp_combi() == ilp_combi
    assert str(exc) == (
        'The Find the best single copy regions problem is unfeasible:\n'
        '\t* ILP codes: ir-sc\n'
        '\t* Status: Infeasible'
    )


def test_not_a_circuit():
    """Test NotACircuit exception."""
    exc = NotACircuit()
    assert str(exc) == 'The found path is not a circuit'


def test_no_solution():
    """Test NoSolution exception."""
    exc = NoSolution()
    assert str(exc) == 'There is no solution'
