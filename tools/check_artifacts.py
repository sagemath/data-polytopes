#!/usr/bin/env python3
"""Verify that built wheels and source distributions contain all data files."""

from __future__ import annotations

import argparse
import tarfile
import zipfile
from pathlib import Path


VERSION = "20170220.0"
PACKAGE = "sage_data_polytopes"
DATA_FILES = {
    "Full2d/zzdb.info",
    "Full2d/zzdb.v03",
    "Full2d/zzdb.v04",
    "Full2d/zzdb.v05",
    "Full2d/zzdb.v06",
    "Full3d/zzdb.info",
    "Full3d/zzdb.v04",
    "Full3d/zzdb.v05",
    "Full3d/zzdb.v06",
    "Full3d/zzdb.v07",
    "Full3d/zzdb.v08",
    "Full3d/zzdb.v09",
    "Full3d/zzdb.v10",
    "Full3d/zzdb.v11",
    "Full3d/zzdb.v12",
    "Full3d/zzdb.v13",
    "reflexive_polytopes_2d",
    "reflexive_polytopes_3d",
}


def _wheel_data(names: set[str]) -> set[str]:
    prefix = f"{PACKAGE}/data/"
    return {name.removeprefix(prefix) for name in names if name.startswith(prefix)}


def _sdist_data(names: set[str]) -> set[str]:
    marker = f"/src/{PACKAGE}/data/"
    return {name.split(marker, 1)[1] for name in names if marker in name}


def check_wheel(path: Path) -> None:
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
    assert _wheel_data(names) == DATA_FILES
    assert f"{PACKAGE}/__init__.py" in names
    dist_info = f"{PACKAGE}-{VERSION}.dist-info"
    assert f"{dist_info}/METADATA" in names
    assert f"{dist_info}/licenses/LICENSE" in names
    assert f"{dist_info}/licenses/DATA_LICENSES.md" in names


def check_sdist(path: Path) -> None:
    with tarfile.open(path, "r:gz") as archive:
        names = {member.name for member in archive.getmembers() if member.isfile()}
    assert _sdist_data(names) == DATA_FILES
    root = f"sage_data_polytopes-{VERSION}"
    for name in (
        "pyproject.toml",
        "MANIFEST.in",
        "README.md",
        "LICENSE",
        "DATA_LICENSES.md",
        f"src/{PACKAGE}/__init__.py",
        "tests/test_resources.py",
        "tests/test_catalogues.py",
        "tools/check_artifacts.py",
    ):
        assert f"{root}/{name}" in names


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifacts", type=Path, nargs="+")
    args = parser.parse_args()
    found = {"wheel": False, "sdist": False}
    for artifact in args.artifacts:
        if artifact.suffix == ".whl":
            check_wheel(artifact)
            found["wheel"] = True
        elif artifact.name.endswith(".tar.gz"):
            check_sdist(artifact)
            found["sdist"] = True
        else:
            raise ValueError(f"unsupported artifact: {artifact}")
        print(f"verified {artifact}")
    assert all(found.values()), "pass at least one wheel and one source distribution"


if __name__ == "__main__":
    main()
