from __future__ import annotations

import hashlib
from importlib.metadata import version

import pytest

import polytope_databases as data


EXPECTED_FILES = {
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


def test_version() -> None:
    assert data.__version__ == "20170220.2"
    assert version("polytope-databases") == data.__version__


def test_manifest_and_hashes() -> None:
    assert len(data.DATA_FILES) == 18
    assert set(data.DATA_FILES) == EXPECTED_FILES
    assert set(data.DATA_SHA256) == EXPECTED_FILES
    for name, expected_hash in data.DATA_SHA256.items():
        contents = data.resource(*name.split("/")).read_bytes()
        assert hashlib.sha256(contents).hexdigest() == expected_hash
    data.verify_data()


def test_low_level_open_api() -> None:
    with data.open_resource("reflexive_polytopes_2d", mode="r") as stream:
        assert stream.readline() == "3 2\n"
    with data.open_resource("Full2d", "zzdb.v03") as stream:
        assert stream.read() == bytes.fromhex("0fb700bc00")


@pytest.mark.parametrize(
    "parts",
    [(), ("",), (".",), ("..",), ("Full3d/zzdb.info",), ("Full3d\\zzdb.info",)],
)
def test_resource_rejects_unsafe_or_ambiguous_names(parts) -> None:
    with pytest.raises(ValueError):
        data.resource(*parts)


def test_missing_resource() -> None:
    with pytest.raises(FileNotFoundError):
        data.resource("missing")


def test_resources_are_read_only() -> None:
    with pytest.raises(ValueError):
        data.open_resource("reflexive_polytopes_2d", mode="w")
    with pytest.raises(ValueError):
        data.open_resource("reflexive_polytopes_2d", mode="rb", encoding="utf-8")
    with pytest.raises(IsADirectoryError):
        data.open_resource("Full2d")


def test_real_path_contexts() -> None:
    with data.reflexive_polytopes_path(2) as path:
        assert path.is_file()
        assert path.read_text(encoding="ascii").startswith("3 2\n")
    with data.palp_database_path(3) as path:
        assert path.is_dir()
        assert (path / "zzdb.info").read_bytes().startswith(b"3  10 13 10")


@pytest.mark.parametrize("dim", [0, 1, 4, True, 2.0, "3"])
@pytest.mark.parametrize(
    "accessor",
    [data.reflexive_polytopes, data.palp_database],
)
def test_dimension_validation(dim, accessor) -> None:
    with pytest.raises(ValueError, match="dimension must be 2 or 3"):
        accessor(dim)
