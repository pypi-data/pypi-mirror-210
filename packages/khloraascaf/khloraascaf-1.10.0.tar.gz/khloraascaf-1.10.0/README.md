# Khloraa: scaffolding stage

[![Latest release](https://gitlab.com/khloraa_scaffolding/khloraa_scaffolding/-/badges/release.svg)](https://gitlab.com/khloraa_scaffolding/khloraa_scaffolding/-/releases)
[![PyPI version](https://badge.fury.io/py/khloraascaf.svg)](https://badge.fury.io/py/khloraascaf)
[![Coverage report](https://gitlab.com/khloraa_scaffolding/khloraa_scaffolding/badges/main/coverage.svg)](https://gitlab.com/khloraa_scaffolding/khloraa_scaffolding/-/commits/main)
[![Pylint score](https://gitlab.com/khloraa_scaffolding/khloraa_scaffolding/-/jobs/artifacts/main/raw/pylint/pylint.svg?job=pylint)](https://gitlab.com/khloraa_scaffolding/khloraa_scaffolding/-/commits/main)
[![Mypy](https://gitlab.com/khloraa_scaffolding/khloraa_scaffolding/-/jobs/artifacts/main/raw/mypy/mypy.svg?job=mypy)](https://gitlab.com/khloraa_scaffolding/khloraa_scaffolding/-/commits/main)
[![Pipeline status](https://gitlab.com/khloraa_scaffolding/khloraa_scaffolding/badges/main/pipeline.svg)](https://gitlab.com/khloraa_scaffolding/khloraa_scaffolding/-/commits/main)
[![Documentation Status](https://readthedocs.org/projects/khloraa_scaffolding/badge/?version=latest)](https://khloraa-scaffolding.readthedocs.io/en/latest)

 <img src="docs/img/logo_transp.png" alt="khloraascaf logo"
width="200" height="200">

`khloraascaf` is a Python3 package that implements a dedicated scaffolding method for chloroplast genomes.

From input data files, it computes combinations of Integer Linear Programming (ILP) programs and write the result of the best one in output files.

Please have a look to the [documentation website](https://khloraa-scaffolding.readthedocs.io) for more details.


## Quick installation

To install the `khloraascaf` package from the [PyPI repository](https://pypi.org/project/khloraascaf/), run the `pip` command :
```sh
pip install khloraascaf
```

You can find more installation details in the [docs/src/install.md](docs/src/install.md) file.


## Quick usage example

```python
from pathlib import Path

from khloraascaf import SOLVER_CBC, IOConfig, MetadataAllSolutions, scaffolding


# ---------------------------------------------------------------------------- #
# Run the example
# ---------------------------------------------------------------------------- #
#
# Prepare the scaffolding result directory
#
outdir = Path('scaffolding_result')
outdir.mkdir(exist_ok=True)
#
# Compute the scaffolding using the assembly data
#
outdir_gen = scaffolding(
    Path('tests/data/ir_sc/contig_attrs.tsv'),
    Path('tests/data/ir_sc/contig_links.tsv'),
    'C0',
    solver=SOLVER_CBC,
    outdir=outdir,
)
#
# khloraascaf creates a directory with a unique name
#   to put all the files it has created
#
assert outdir_gen in outdir.glob('*')
print(outdir_gen)

# ---------------------------------------------------------------------------- #
# Dive into the results
# ---------------------------------------------------------------------------- #
#
# Use metadata class to easily dive into the results
# (you can also see by hand the solutions.yaml file that has been produced)
#
all_solutions_metadata = MetadataAllSolutions.from_run_directory(outdir_gen)
#
# * How many solutions the scaffolding has produced?
#
print(len(all_solutions_metadata))
#   = 1, let pick its metadata
sol_metadata = tuple(all_solutions_metadata)[0]
#
# See which files the scaffolding has produced:
#
files = set(outdir_gen.glob('*'))
assert len(files) == 4
#
# * The list of oriented contigs for each region
#
assert sol_metadata.contigs_of_regions() in files
#
# * The list of oriented regions
#
assert sol_metadata.map_of_regions() in files
#
# * YAML file containing all the arguments and options you used
#   to run khloraascaf
#
assert outdir_gen / IOConfig.YAML_FILE in files
#
# * YAML file that contains metadata on the solutions
#
assert outdir_gen / MetadataAllSolutions.YAML_FILE in files
```


## Changelog

You can refer to the [docs/src/changelog.md](docs/src/changelog.md) file for details.


## What next?

Find a list of ideas in the [docs/src/todo.md](docs/src/todo.md) file.


## Contributing

* If you find any errors, missing documentation or test, or you want to discuss features you would like to have, please post an issue (with the corresponding predefined template) [here](https://gitlab.com/khloraa_scaffolding/khloraa_scaffolding/-/issues).
* If you want to help me code, please post an issue or contact me. You can find coding convention in the [docs/src/contributing.md](docs/src/contributing.md) file.


## References

<!-- DOCU must update reference -->

* A part of the scaffolding method is described in this preprint:
    > 📰 Victor Epain, Dominique Lavenier, and Rumen Andonov, ‘Inverted Repeats Scaffolding for a Dedicated Chloroplast Genome Assembler’, 3 June 2022, https://doi.org/10.4230/LIPIcs.


## Licence

This work is licensed under a [GNU-GPLv3 licence](LICENCE).