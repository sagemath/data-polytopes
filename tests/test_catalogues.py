from __future__ import annotations

import pytest

from sage_data_polytopes import open_reflexive_polytopes, palp_database


def _catalogue_size(dimension: int) -> int:
    count = 0
    with open_reflexive_polytopes(dimension) as stream:
        lines = iter(stream)
        for header in lines:
            rows, columns = (int(value) for value in header.split())
            assert columns == dimension
            assert rows >= dimension + 1
            for _ in range(rows):
                coordinates = [int(value) for value in next(lines).split()]
                assert len(coordinates) == dimension
            count += 1
    return count


@pytest.mark.parametrize("dimension, expected", [(2, 16), (3, 4319)])
def test_plain_text_catalogue_is_complete_and_parseable(dimension, expected) -> None:
    assert _catalogue_size(dimension) == expected


@pytest.mark.parametrize(
    "dimension, expected_names",
    [
        (2, {"zzdb.info", "zzdb.v03", "zzdb.v04", "zzdb.v05", "zzdb.v06"}),
        (
            3,
            {
                "zzdb.info",
                "zzdb.v04",
                "zzdb.v05",
                "zzdb.v06",
                "zzdb.v07",
                "zzdb.v08",
                "zzdb.v09",
                "zzdb.v10",
                "zzdb.v11",
                "zzdb.v12",
                "zzdb.v13",
            },
        ),
    ],
)
def test_palp_database_files_are_readable(dimension, expected_names) -> None:
    directory = palp_database(dimension)
    files = {entry.name: entry for entry in directory.iterdir() if entry.is_file()}
    assert set(files) == expected_names
    assert all(entry.read_bytes() for entry in files.values())
