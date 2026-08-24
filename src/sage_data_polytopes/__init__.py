"""Packaged SageMath databases of two- and three-dimensional polytopes.

The public helpers return :mod:`importlib.resources` ``Traversable`` objects or
context managers for real filesystem paths.  The package performs no network
access and does not depend on SageMath.
"""

from __future__ import annotations

import hashlib
import os
import operator
import shutil
from contextlib import contextmanager
from importlib import resources
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import IO, Iterator, Mapping, Union

try:  # ``importlib.resources.abc`` was added after Python 3.9.
    from importlib.resources.abc import Traversable
except ImportError:  # pragma: no cover - exercised only on Python 3.9/3.10
    from importlib.abc import Traversable  # type: ignore[attr-defined,no-redef]

__version__ = "20170220.0"

DATA_FILES = (
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
)

DATA_SHA256: Mapping[str, str] = {
    "Full2d/zzdb.info": "719ff58ca68984379be5962772983de912a8d74037173ed5c965268c135adaac",
    "Full2d/zzdb.v03": "dde5ff0e7fd5c109d0aca7c01d1e2660e5f31af1199e8584d37cf9b878354b2c",
    "Full2d/zzdb.v04": "0e81c83a04f4eb45e4cc393b36923e55844ddc4d7a23c8e01fb0095d1b760371",
    "Full2d/zzdb.v05": "b7f853e6fc6e10c3362a6e4c9eb63ddca72c1832481ce06bd6d4629bb58bcb35",
    "Full2d/zzdb.v06": "1aef85f64ccf4318bc3f25c20a4f5f3f1c635bebc36772d89c95ac639340c575",
    "Full3d/zzdb.info": "b76c164ca39e018c62a2387443ff7940edba86615c13409c92e82094cf12e241",
    "Full3d/zzdb.v04": "15545d51cc41c1dc70e543e5471cb14eff480da792a520c9d6041efef699a591",
    "Full3d/zzdb.v05": "a787c47c6db5077bf54110957bc1ceb9538170aa0cd1e50c399814ea86e61c5b",
    "Full3d/zzdb.v06": "1f86ff7cb8478fdf768547f848179da4f73587d5bd77672498a241596a42abe9",
    "Full3d/zzdb.v07": "5aa55925b1eb46309bb7c70ce8dd2da3c2ae137390375ba79eac003c4ca65dc9",
    "Full3d/zzdb.v08": "97ff70bff251043cea9978112de9c604ed6a5624438c3ee47876fd2aab601a78",
    "Full3d/zzdb.v09": "d770b9ee7b1be356c451e9e6d77249d9afd59329b52ff34d4dd1e0cff58d6995",
    "Full3d/zzdb.v10": "44d193a4765baa0fe442301a5e1b65f909d76d2c6980b9f140214909a4cc734c",
    "Full3d/zzdb.v11": "696051521ff2a732d3c0e401b77922362eef5475158c84c1bb31a7533fdecd7c",
    "Full3d/zzdb.v12": "92a9a3bcbf31f415bd45b3e1ee5516e0e318d5d63d0538b83d1712f5889e410c",
    "Full3d/zzdb.v13": "f36361bf277890f4c84559520e36022449c53280d363edd883cd4fabe0d71577",
    "reflexive_polytopes_2d": "f0e47311eb365f700e2a03a6b061fee85d44f1d3937acff32876723f47ebedb4",
    "reflexive_polytopes_3d": "1d590ab17bb166084d87467123c7c9ff189dd15b42e4bf4d5df6790ffd10fed3",
}


def data_root() -> Traversable:
    """Return the root of the packaged data as a Traversable resource."""

    return resources.files(__package__).joinpath("data")


def _resource_parts(parts: tuple[Union[str, os.PathLike[str]], ...]) -> tuple[str, ...]:
    if not parts:
        raise ValueError("at least one relative resource name is required")
    result = []
    for value in parts:
        part = os.fspath(value)
        if (
            not part
            or part in {".", ".."}
            or os.path.isabs(part)
            or "/" in part
            or "\\" in part
        ):
            raise ValueError(f"invalid resource path component: {part!r}")
        result.append(part)
    return tuple(result)


def resource(*parts: Union[str, os.PathLike[str]]) -> Traversable:
    """Return one packaged resource.

    Each argument must be one relative path component. For example,
    ``resource("Full3d", "zzdb.info")`` returns the PALP metadata file.
    """

    target = data_root().joinpath(*_resource_parts(parts))
    if not (target.is_file() or target.is_dir()):
        raise FileNotFoundError("/".join(os.fspath(part) for part in parts))
    return target


def open_resource(
    *parts: Union[str, os.PathLike[str]],
    mode: str = "rb",
    encoding: str | None = None,
    errors: str | None = None,
    newline: str | None = None,
) -> IO:
    """Open a packaged resource for reading.

    Text mode defaults to UTF-8. Write and update modes are rejected because
    installed package resources are immutable.
    """

    if any(flag in mode for flag in "wax+") or "r" not in mode:
        raise ValueError("package resources can only be opened for reading")
    target = resource(*parts)
    if not target.is_file():
        raise IsADirectoryError("/".join(os.fspath(part) for part in parts))
    if "b" in mode:
        if any(value is not None for value in (encoding, errors, newline)):
            raise ValueError("encoding, errors, and newline require text mode")
        return target.open(mode)
    return target.open(
        mode,
        encoding=encoding or "utf-8",
        errors=errors,
        newline=newline,
    )


def _copy_directory(source: Traversable, destination: Path) -> None:
    destination.mkdir()
    for child in source.iterdir():
        output = destination / child.name
        if child.is_dir():
            _copy_directory(child, output)
        elif child.is_file():
            with child.open("rb") as input_stream, output.open("wb") as output_stream:
                shutil.copyfileobj(input_stream, output_stream)


@contextmanager
def resource_path(*parts: Union[str, os.PathLike[str]]) -> Iterator[Path]:
    """Yield a real filesystem path for a packaged file or directory.

    Keep the context open while using the path. A temporary copy is created
    when an import loader does not expose resources directly on the filesystem.
    """

    target = resource(*parts)
    if isinstance(target, Path):
        yield target
        return
    if target.is_file():
        with resources.as_file(target) as path:
            yield path
        return
    with TemporaryDirectory(prefix="sage-data-polytopes-") as temporary:
        path = Path(temporary) / target.name
        _copy_directory(target, path)
        yield path


def _dimension(value: object) -> int:
    if isinstance(value, bool):
        raise ValueError("dimension must be 2 or 3")
    try:
        dimension = operator.index(value)  # type: ignore[arg-type]
    except TypeError as error:
        raise ValueError("dimension must be 2 or 3") from error
    if dimension not in (2, 3):
        raise ValueError("dimension must be 2 or 3")
    return dimension


def reflexive_polytopes(dim: object) -> Traversable:
    """Return the plain-text reflexive-polytope catalogue for dimension 2 or 3."""

    return resource(f"reflexive_polytopes_{_dimension(dim)}d")


def open_reflexive_polytopes(dim: object, *, encoding: str = "ascii") -> IO:
    """Open a reflexive-polytope catalogue as a text stream."""

    return open_resource(
        f"reflexive_polytopes_{_dimension(dim)}d", mode="r", encoding=encoding
    )


@contextmanager
def reflexive_polytopes_path(dim: object) -> Iterator[Path]:
    """Yield a real filesystem path to a plain-text polytope catalogue."""

    with resource_path(f"reflexive_polytopes_{_dimension(dim)}d") as path:
        yield path


def palp_database(dim: object) -> Traversable:
    """Return the PALP database directory for dimension 2 or 3."""

    return resource(f"Full{_dimension(dim)}d")


@contextmanager
def palp_database_path(dim: object) -> Iterator[Path]:
    """Yield a real filesystem path to a PALP database directory."""

    with resource_path(f"Full{_dimension(dim)}d") as path:
        yield path


def verify_data() -> None:
    """Raise an exception unless all packaged data matches the release manifest."""

    actual_files = []
    for directory in ("Full2d", "Full3d"):
        actual_files.extend(
            f"{directory}/{item.name}"
            for item in resource(directory).iterdir()
            if item.is_file()
        )
    actual_files.extend(
        name for name in ("reflexive_polytopes_2d", "reflexive_polytopes_3d")
        if resource(name).is_file()
    )
    if tuple(sorted(actual_files)) != tuple(sorted(DATA_FILES)):
        raise RuntimeError("packaged data file manifest does not match DATA_FILES")
    for name, expected in DATA_SHA256.items():
        digest = hashlib.sha256(resource(*name.split("/")).read_bytes()).hexdigest()
        if digest != expected:
            raise RuntimeError(f"checksum mismatch for {name}: {digest}")


__all__ = [
    "DATA_FILES",
    "DATA_SHA256",
    "data_root",
    "open_reflexive_polytopes",
    "open_resource",
    "palp_database",
    "palp_database_path",
    "reflexive_polytopes",
    "reflexive_polytopes_path",
    "resource",
    "resource_path",
    "verify_data",
]
