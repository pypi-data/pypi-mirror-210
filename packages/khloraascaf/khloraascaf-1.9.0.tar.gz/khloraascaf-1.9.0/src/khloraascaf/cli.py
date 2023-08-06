# -*- coding=utf-8 -*-

"""Command Line Interface library and configs."""

from argparse import ArgumentParser, Namespace

from khloraascaf.inputs import (
    INSTANCE_NAME_DEF,
    MULT_UPB_DEF,
    OUTDIR_DEF,
    PRESSCORE_UPB_DEF,
    SOLVER_CBC,
    SOLVER_GUROBI,
    MultT,
    PresScoreT,
)


# ============================================================================ #
#                                   CONSTANTS                                  #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                                   Arguments                                  #
# ---------------------------------------------------------------------------- #
ARG_CONTIG_ATTRS = 'contig_attributes'
_ARG_CONTIG_ATTRS_TYPE = str  # pylint: disable=invalid-name
_ARG_CONTIG_ATTRS_HELP = (
    'The multiplicities and the presence score of the contigs'
)

ARG_CONTIG_LINKS = 'contig_links'
_ARG_CONTIG_LINKS_TYPE = str  # pylint: disable=invalid-name
_ARG_CONTIG_LINKS_HELP = 'The links between the oriented contigs'

ARG_CONTIG_STARTER = 'starter_id'
_ARG_CONTIG_STARTER_TYPE = str  # pylint: disable=invalid-name
_ARG_CONTIG_STARTER_HELP = 'The identifier of the starter contig'

# ---------------------------------------------------------------------------- #
#                                    Options                                   #
# ---------------------------------------------------------------------------- #
OPT_MULT_UPB = 'multiplicity_upperbound'
_OPT_MULT_UPB_FLAG = ('--mult-upbound',)
_OPT_MULT_UPB_TYPE = MultT  # pylint: disable=invalid-name
_OPT_MULT_UPB_HELP = 'The upper bound for unknown multiplicities'

OPT_PRESSCORE_UPB = 'presence_score_upperbound'
_OPT_PRESSCORE_UPB_FLAG = ('--presscore-upbound',)
_OPT_PRESSCORE_UPB_TYPE = PresScoreT  # pylint: disable=invalid-name
_OPT_PRESSCORE_UPB_HELP = 'The upper bound for unknown presence score'

OPT_SOLVER = 'solver'
_OPT_SOLVER_FLAG = ('--solver',)
_OPT_SOLVER_TYPE = str  # pylint: disable=invalid-name
_OPT_SOLVER_CHOICES = (SOLVER_CBC, SOLVER_GUROBI)
_OPT_SOLVER_HELP = 'The MILP solver to use'

OPT_OUTDIR = 'output_directory'
_OPT_OUTDIR_FLAG = ('--out-directory',)
_OPT_OUTDIR_TYPE = str  # pylint: disable=invalid-name
_OPT_OUTDIR_HELP = 'The output directory path, generated if not given'

OPT_INSTANCE_NAME = 'instance_name'
_OPT_INSTANCE_NAME_FLAG = ('--instance-name',)
_OPT_INSTANCE_NAME_TYPE = str  # pylint: disable=invalid-name
_OPT_INSTANCE_NAME_HELP = 'Custom prefix for outputs'

OPT_OUTDEBUG = 'debug'
_OPT_OUTDEBUG_FLAG = ('--debug',)
_OPT_OUTDEBUG_HELP = 'Outputs debugs'


# ============================================================================ #
#                                   FUNCTIONS                                  #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                              Command Line Parser                             #
# ---------------------------------------------------------------------------- #
def arguments_cmdline() -> Namespace:
    """Set arguments in command line.

    Returns
    -------
    Namespace
        Parsed command line
    """
    # ------------------------------------------------------------------------ #
    # Programm
    # ------------------------------------------------------------------------ #
    argparser = ArgumentParser(
        prog='python3.9 -m khloraascaf',
        description='Scaffolding python module of chloroplast genome assembly',
    )

    # ------------------------------------------------------------------------ #
    # Arguments
    # ------------------------------------------------------------------------ #
    argparser.add_argument(
        ARG_CONTIG_ATTRS,
        type=_ARG_CONTIG_ATTRS_TYPE,
        help=_ARG_CONTIG_ATTRS_HELP,
    )
    argparser.add_argument(
        ARG_CONTIG_LINKS,
        type=_ARG_CONTIG_LINKS_TYPE,
        help=_ARG_CONTIG_LINKS_HELP,
    )
    argparser.add_argument(
        ARG_CONTIG_STARTER,
        type=_ARG_CONTIG_STARTER_TYPE,
        help=_ARG_CONTIG_STARTER_HELP,
    )

    # ------------------------------------------------------------------------ #
    # Options
    # ------------------------------------------------------------------------ #
    argparser.add_argument(
        *_OPT_MULT_UPB_FLAG,
        dest=OPT_MULT_UPB,
        type=_OPT_MULT_UPB_TYPE,
        default=MULT_UPB_DEF,
        help=_OPT_MULT_UPB_HELP,
    )
    argparser.add_argument(
        *_OPT_PRESSCORE_UPB_FLAG,
        dest=OPT_PRESSCORE_UPB,
        type=_OPT_PRESSCORE_UPB_TYPE,
        default=PRESSCORE_UPB_DEF,
        help=_OPT_PRESSCORE_UPB_HELP,
    )
    argparser.add_argument(
        *_OPT_SOLVER_FLAG,
        dest=OPT_SOLVER,
        type=_OPT_SOLVER_TYPE,
        choices=_OPT_SOLVER_CHOICES,
        default=SOLVER_CBC,
        help=_OPT_SOLVER_HELP,
    )
    argparser.add_argument(
        *_OPT_OUTDIR_FLAG,
        dest=OPT_OUTDIR,
        type=_OPT_OUTDIR_TYPE,
        default=OUTDIR_DEF,
        help=_OPT_OUTDIR_HELP,
    )
    argparser.add_argument(
        *_OPT_INSTANCE_NAME_FLAG,
        dest=OPT_INSTANCE_NAME,
        type=_OPT_INSTANCE_NAME_TYPE,
        default=INSTANCE_NAME_DEF,
        help=_OPT_INSTANCE_NAME_HELP,
    )
    argparser.add_argument(
        *_OPT_OUTDEBUG_FLAG,
        dest=OPT_OUTDEBUG,
        action='store_true',
        help=_OPT_OUTDEBUG_HELP,
    )
    return argparser.parse_args()
