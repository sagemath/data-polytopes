# Data provenance and licensing notes

This distribution contains the 18 data files from SageMath's
`polytopes_db-20170220` package. The Python resource-access code and packaging
files in this repository are offered under GPL-2.0-or-later; `LICENSE` contains
the full GPL version 2 text.

## Reflexive-polytope data

SageMath's `build/pkgs/polytopes_db/SPKG.rst` describes the package as lists of
two- and three-dimensional reflexive polytopes. It states that the list of
three-dimensional polytopes was originally obtained by Maximilian Kreuzer and
Harald Skarke using their PALP software, and identifies this upstream page:

<https://hep.itp.tuwien.ac.at/~kreuzer/CY/CYpalp.html>

That package description labels the license as `GPL`. However, SageMath's
top-level `COPYING.txt` separately records `polytopes_db` as `None (database)`.
Those two records do not establish unambiguous redistribution terms for the
database contents themselves.

**Release blocker:** before publishing this distribution to PyPI, confirm the
applicable terms with the SageMath and/or original data maintainers, retain the
resulting permission or license notice here, and adjust the project metadata if
needed. The GPL declaration in `pyproject.toml` must not be interpreted as
asserting rights over data whose terms have not yet been confirmed.

## Scope

No four-dimensional polytope data is included. In particular, SageMath's
separate `polytopes_db_4d` package and its `Hodge4d` data are out of scope.
