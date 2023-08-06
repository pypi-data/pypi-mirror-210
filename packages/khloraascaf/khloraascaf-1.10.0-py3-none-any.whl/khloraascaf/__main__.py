# -*- coding=utf-8 -*-

"""Main when khloraascaff is launched in command line."""

from argparse import Namespace
from pathlib import Path

from khloraascaf.cli import (
    ARG_CONTIG_ATTRS,
    ARG_CONTIG_LINKS,
    ARG_CONTIG_STARTER,
    OPT_INSTANCE_NAME,
    OPT_MULT_UPB,
    OPT_OUTDEBUG,
    OPT_OUTDIR,
    OPT_PRESSCORE_UPB,
    OPT_SOLVER,
    arguments_cmdline,
)
from khloraascaf.scaffolding_methods import scaffolding


# ============================================================================ #
#                                     MAIN                                     #
# ============================================================================ #
if __name__ == '__main__':
    # ------------------------------------------------------------------------ #
    # Parse command line arguments
    # ------------------------------------------------------------------------ #
    args: Namespace = arguments_cmdline()

    # ------------------------------------------------------------------------ #
    # Run the scaffolding step
    # ------------------------------------------------------------------------ #
    output_dir_gen = scaffolding(
        Path(getattr(args, ARG_CONTIG_ATTRS)),
        Path(getattr(args, ARG_CONTIG_LINKS)),
        getattr(args, ARG_CONTIG_STARTER),
        multiplicity_upperbound=getattr(args, OPT_MULT_UPB),
        presence_score_upperbound=getattr(args, OPT_PRESSCORE_UPB),
        solver=getattr(args, OPT_SOLVER),
        outdir=Path(getattr(args, OPT_OUTDIR)),
        instance_name=getattr(args, OPT_INSTANCE_NAME),
        debug=getattr(args, OPT_OUTDEBUG),
    )
    #
    # To get the output directory path from shell
    #
    # TODO logging here output_dir_gen
    print(output_dir_gen)
