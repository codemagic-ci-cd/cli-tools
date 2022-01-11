import argparse
from unittest import mock

import pytest

from codemagic.cli.argument import CommonArgumentTypes
from codemagic.cli.argument.common_argument_types import pathlib


@mock.patch.object(pathlib.Path, 'exists')
@mock.patch.object(pathlib.Path, 'is_dir')
def test_path_does_not_exist(mock_is_dir, mock_exists):
    # TODO: parametrize return values for mocks
    mock_exists.return_value = False
    mock_is_dir.return_value = False
    dir_path = CommonArgumentTypes.maybe_dir('/this/path/does/not/exist')
    assert isinstance(dir_path, pathlib.Path)
    assert mock_exists.called is True
    assert mock_exists.call_count == 5
    assert mock_is_dir.called is True
    assert mock_is_dir.call_count == 1


@mock.patch.object(pathlib.Path, 'is_dir')
def test_dir_exists(mock_is_dir):
    mock_is_dir.return_value = True
    dir_path = CommonArgumentTypes.maybe_dir('/this/path/exist_and_is_dir')
    assert isinstance(dir_path, pathlib.Path)
    assert mock_is_dir.called is True
    assert mock_is_dir.call_count == 1


@mock.patch.object(pathlib.Path, 'exists')
@mock.patch.object(pathlib.Path, 'is_dir')
def test_not_dir_but_exists(mock_is_dir, mock_exists):
    mock_is_dir.return_value = False
    mock_exists.return_value = True
    with pytest.raises(argparse.ArgumentTypeError):
        CommonArgumentTypes.maybe_dir('/this/path/exists/and/is/not/a/directory')


@mock.patch.object(pathlib.Path, 'exists')
@mock.patch.object(pathlib.Path, 'is_dir')
def test_path_contains_file(mock_is_dir, mock_exists):
    """
    Test for cases when directory structure is as
    dir/
        file
    and given path is dir/file/another_dir
    """
    mock_is_dir.return_value = False
    mock_exists.return_value = False
    # TODO
    # with mock.patch(pathlib) as mock_path
    # with pytest.raises(argparse.ArgumentTypeError):
    #     CommonArgumentTypes.maybe_dir('/existing_dir/existing_file/subdir')
