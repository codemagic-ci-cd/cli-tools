import pathlib
from distutils.version import LooseVersion
from unittest import mock

import pytest

from codemagic.models import Xcode


@pytest.fixture
def mock_developer_dir():
    return pathlib.Path(__file__).parent / 'mocks' / 'mock_xcode/Contents/Developer'


def test_get_selected(mock_developer_dir):
    with mock.patch('codemagic.models.xcode.subprocess') as mock_subprocess, \
            mock.patch('codemagic.models.xcode.shutil') as mock_shutil:
        mock_shutil.which = lambda *args: args
        mock_subprocess.check_output.return_value = str(mock_developer_dir).encode()
        xcode = Xcode.get_selected()

    assert xcode.developer_dir == mock_developer_dir


def test_version(mock_developer_dir):
    xcode = Xcode(mock_developer_dir)
    assert xcode.version == LooseVersion('12.0.1')


def test_build_version(mock_developer_dir):
    xcode = Xcode(mock_developer_dir)
    assert xcode.build_version == '12A7300'
