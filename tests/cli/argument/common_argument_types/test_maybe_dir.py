import argparse
import pathlib
from tempfile import NamedTemporaryFile
from tempfile import TemporaryDirectory
from unittest import mock

import pytest

from codemagic.cli.argument import CommonArgumentTypes
from codemagic.cli.argument import common_argument_types


@mock.patch.object(common_argument_types.pathlib.Path, 'exists')
@mock.patch.object(common_argument_types.pathlib.Path, 'is_dir')
def test_path_and_parents_do_not_exist(mock_is_dir, mock_exists):
    given_path = '/this/path/does/not/exist'
    mock_exists.return_value = False  # No path exists
    mock_is_dir.return_value = False  # No path is a directory
    dir_path = CommonArgumentTypes.maybe_dir(given_path)
    assert str(dir_path) == given_path


@mock.patch.object(common_argument_types.pathlib.Path, 'is_dir')
def test_dir_exists(mock_is_dir):
    given_path = '/this/path/exist_and_is_dir'
    mock_is_dir.return_value = True  # All paths are directories
    dir_path = CommonArgumentTypes.maybe_dir(given_path)
    assert str(dir_path) == given_path


@mock.patch.object(common_argument_types.pathlib.Path, 'exists')
@mock.patch.object(common_argument_types.pathlib.Path, 'is_dir')
def test_not_dir_but_exists(mock_is_dir, mock_exists):
    mock_is_dir.return_value = False  # No paths are directories
    mock_exists.return_value = True  # But paths exists
    with pytest.raises(argparse.ArgumentTypeError) as error_info:
        CommonArgumentTypes.maybe_dir('/this/path/exists/and/is/not/a/directory')
    assert 'exists but is not a directory' in str(error_info.value)


@pytest.mark.parametrize('path_suffixes', [
    ('d1',),
    ('d1', 'd2'),
    ('d1', 'd2', 'd3'),
])
def test_given_path_contains_existing_file(path_suffixes):
    """
    Test for cases when directory structure is as
    dir/
        file
    and given path is dir/file/another_dir
    """
    with TemporaryDirectory() as td:
        with NamedTemporaryFile(dir=td) as tf:
            invalid_dir_path = pathlib.Path(tf.name, *path_suffixes).resolve()
            with pytest.raises(argparse.ArgumentTypeError) as error_info:
                CommonArgumentTypes.maybe_dir(str(invalid_dir_path))
    expected_error = 'cannot be used as a directory as it contains a path to an existing file'
    assert expected_error in str(error_info.value)


@pytest.mark.parametrize('path_suffixes', [
    ('invalid_dir',),
    ('d1', 'd2'),
    ('d1', 'd2', 'd3'),
])
def test_given_path_contains_existing_dir(path_suffixes):
    """
    Test for cases when directory structure is as
    dir1/
        dir2
    and given path is dir1/dir2/dir3
    """
    with TemporaryDirectory() as td:
        valid_dir_path = pathlib.Path(td, *path_suffixes).resolve()
        dir_path = CommonArgumentTypes.maybe_dir(str(valid_dir_path))
    assert str(dir_path) == str(valid_dir_path)
