# sage-data-polytopes

`sage-data-polytopes` packages the SageMath databases of two- and
three-dimensional reflexive lattice polytopes as an ordinary, pure-Python
distribution. It has no dependency on SageMath and never accesses the network
at build time or run time.

The distribution contains two representations of the same catalogues:

- plain-text lists containing 16 two-dimensional and 4,319 three-dimensional
  reflexive polytopes; and
- the `Full2d` and `Full3d` databases used by PALP.

The much larger four-dimensional database is deliberately out of scope.

## Installation

```console
python -m pip install sage-data-polytopes
```

## Resource API

The API is based on `importlib.resources`, so callers do not need to know where
the wheel was installed:

```python
from sage_data_polytopes import (
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
Harald Skarke using PALP. See [DATA_LICENSES.md](DATA_LICENSES.md) for the
available provenance and an important licensing caveat that must be resolved
before the first public release.

## Development

```console
python -m pip install -e .
python -m pytest
python -m build
python tools/check_artifacts.py dist/*.whl dist/*.tar.gz
```
