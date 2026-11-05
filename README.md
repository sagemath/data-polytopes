# polytope-databases

`polytope-databases` packages the SageMath databases of two- and
three-dimensional reflexive lattice polytopes as an ordinary, pure-Python
distribution. It has no dependency on SageMath and never accesses the network
at build time or run time.

The distribution contains two representations of the same catalogues:

- plain-text lists containing 16 two-dimensional and 4,319 three-dimensional
  reflexive polytopes; and
- the `Full2d` and `Full3d` databases used by PALP.

The much larger four-dimensional database is deliberately out of scope.

## Installation

Requires Python 3.13 or newer.

```console
python -m pip install polytope-databases
```

The Python import name is `polytope_databases`.

## Resource API

The API is based on `importlib.resources`, so callers do not need to know where
the wheel was installed:

```python
from polytope_databases import (
    open_reflexive_polytopes,
    palp_database_path,
    reflexive_polytopes,
)

# A Traversable resource, suitable for read_bytes(), read_text(), and open().
catalogue = reflexive_polytopes(3)

with open_reflexive_polytopes(2) as stream:
    first_header = stream.readline()

# PALP needs a real filesystem directory. Keep the context open while PALP
# uses the path; resources from unusual zip importers may be temporary.
with palp_database_path(3) as directory:
    palp_basename = directory / "zzdb"
```

The lower-level `data_root()`, `resource()`, `open_resource()`, and
`resource_path()` helpers are also public. Only dimensions 2 and 3 are accepted
by the dimension-specific helpers.

## Data provenance and licensing

The three-dimensional list was originally obtained by Maximilian Kreuzer and
Harald Skarke using PALP. See [DATA_LICENSES.md](https://github.com/sagemath/data-polytopes/blob/main/DATA_LICENSES.md) for the
available provenance and an important licensing caveat that must be resolved
before the first public release.

## Releases

Publishing a GitHub Release runs the `Release` GitHub Actions workflow.  It
checks that the tag matches the package version, builds and validates the wheel
and source distribution, smoke-tests the wheel in a clean environment,
attaches both artifacts to the GitHub Release, and publishes them to PyPI
through Trusted Publishing.  The Release tag must be `20170220.2` or
`v20170220.2`.  Configure a PyPI Trusted Publisher for this repository, the
`release.yml` workflow, and the `pypi` environment before the first release.
The PyPI project name is `polytope-databases`, the GitHub owner is
`sagemath`, and the repository name is `data-polytopes`.
Do not publish a release until the data-license caveat above has been resolved.

## Development

```console
python -m pip install -e .
python -m pytest
python -m build
python tools/check_artifacts.py dist/*.whl dist/*.tar.gz
```

## Migration from the previous package

This distribution replaces `sagemath-data-polytopes`. Install `polytope-databases` and change
imports from `sage_data_polytopes` to `polytope_databases`. The resource helpers and
bundled database contents are unchanged. The two distributions use separate
import namespaces and can coexist while consumers migrate.
