from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

import pytest
from codemagic.mixins import PathFinderMixin


@pytest.fixture()
def path_finder() -> PathFinderMixin:
    class PathFinder(PathFinderMixin):
        logger = mock.MagicMock()

    return PathFinder()


@pytest.mark.parametrize(
    "pattern",
    (
        ".",
        "lorem/..",
        "lorem/ipsum/../..",
    ),
)
def test_find_paths_current_dir_pattern(pattern: str, path_finder: PathFinderMixin):
    """
    In case the pattern is not absolute, then globbing is performed from the
    current directory. Ensure that relative paths pointing to current directory
    do not yield anything.
    """
    paths = list(path_finder.find_paths(Path(pattern)))
    assert paths == []


def test_find_paths_parent_dir(path_finder: PathFinderMixin):
    paths = list(path_finder.find_paths(Path("..")))
    assert paths == [Path("..")]


def test_find_paths_absolute_pattern(path_finder: PathFinderMixin):
    with TemporaryDirectory(suffix="_globbing") as td:
        paths = {Path(td, f"file.{i}") for i in range(10)}
        for p in paths:
            p.touch()  # This should be found

        Path(td, "file2.something_else").touch()  # This shouldn't be found
        found_paths = set(path_finder.find_paths(Path(td, "file.*")))

    assert paths == found_paths


def test_find_paths_multiple_patterns(path_finder: PathFinderMixin):
    with TemporaryDirectory(suffix="_globbing") as td:
        paths_1 = {Path(td, f"file.1.{i}") for i in range(10)}
        paths_2 = {Path(td, f"file.2.{i}") for i in range(10)}
        paths = paths_1 | paths_2
        for p in paths:
            p.touch()  # This should be found

        found_paths = set(
            path_finder.find_paths(
                Path(td, "file.1.*"),
                Path(td, "file.2.*"),
            ),
        )

    assert paths == found_paths
