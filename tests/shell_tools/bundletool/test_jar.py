import pathlib
from unittest import mock

import pytest

from codemagic.shell_tools import Bundletool
from codemagic.shell_tools import bundletool as bundletool_module


@pytest.fixture(autouse=True)
def patch_java():
    with mock.patch.object(Bundletool, "_get_java_path"):
        yield


@pytest.fixture(autouse=True)
def reset_default_bundletool_path():
    bundletool_module.DEFAULT_BUNDLETOOL_PATH = None
    yield


def test_existing_custom_jar():
    with mock.patch("pathlib.Path.exists", autospec=True) as mock_exists:
        mock_exists.side_effect = [True]
        jar = pathlib.Path("/path/to/bundletool.jar")
        bundletool = Bundletool(jar=jar)

    assert bundletool.jar == jar


def test_not_existing_custom_jar():
    with mock.patch("pathlib.Path.exists", autospec=True) as mock_exists:
        mock_exists.side_effect = [False]
        with pytest.raises(OSError) as exc_info:
            Bundletool(jar=pathlib.Path("/path/to/bundletool.jar"))

    assert str(exc_info.value) == "/path/to/bundletool.jar does not exist"


def test_existing_included_jar():
    with mock.patch("pathlib.Path.exists", autospec=True) as mock_exists:
        mock_exists.side_effect = [True]

        with mock.patch("codemagic.shell_tools.bundletool.find_included_bundletool_jar", autospec=True) as mock_find:
            included_jar = pathlib.Path("/path/to/included/bundletool.jar")
            mock_find.side_effect = [included_jar]

            bundletool = Bundletool()

    assert bundletool.jar == included_jar


def test_missing_default_and_missing_included_jar():
    bundletool_module.DEFAULT_BUNDLETOOL_PATH = None

    with mock.patch("codemagic.shell_tools.bundletool.find_included_bundletool_jar", autospec=True) as mock_find:
        mock_find.side_effect = IOError("Included Bundletool jar is not available")

        with pytest.raises(OSError) as exc_info:
            Bundletool()

    assert str(exc_info.value) == "Included Bundletool jar is not available"


def test_missing_included_jar_with_existing_default_fallback_jar():
    with mock.patch("pathlib.Path.exists", autospec=True) as mock_exists:
        mock_exists.side_effect = [True]
        default_bundletool_jar = pathlib.Path("/path/to/default/bundletool.jar")
        bundletool_module.DEFAULT_BUNDLETOOL_PATH = default_bundletool_jar

        with mock.patch("codemagic.shell_tools.bundletool.find_included_bundletool_jar", autospec=True) as mock_find:
            mock_find.side_effect = IOError("Included Bundletool jar is not available")
            bundletool = Bundletool()

    assert bundletool.jar == default_bundletool_jar


def test_missing_included_jar_missing_default_fallback_jar():
    with mock.patch("pathlib.Path.exists", autospec=True) as mock_exists:
        mock_exists.side_effect = [False]
        bundletool_module.DEFAULT_BUNDLETOOL_PATH = pathlib.Path("/path/to/default/bundletool.jar")

        with mock.patch("codemagic.shell_tools.bundletool.find_included_bundletool_jar", autospec=True) as mock_find:
            mock_find.side_effect = IOError("Included Bundletool jar is not available")

            with pytest.raises(IOError) as exc_info:
                Bundletool()

    assert str(exc_info.value) == "/path/to/default/bundletool.jar does not exist"
