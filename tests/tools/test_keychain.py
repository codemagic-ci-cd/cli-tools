import argparse
import pathlib
from unittest import mock
from unittest.mock import Mock

import pytest

from codemagic.cli import CliProcess
from codemagic.tools.keychain import Keychain
from codemagic.tools.keychain import KeychainArgument


def mock_find_paths(_self, *args):
    return [*args]


@pytest.mark.parametrize('allowed_apps, allow_all, disallow_all, expected_args, not_expected_args', [
    (['app1', 'app2'], False, False, ['app1', 'app2'], ['-A']),  # Only allow specified apps
    (['app1', 'app2'], True, False, ['-A'], ['app1', 'app2']),  # Allow all apps
    (['app1', 'app2'], False, True, [], ['-A', 'app1', 'app2']),  # Do not allow any apps
])
@mock.patch.object(Keychain, 'find_paths', mock_find_paths)
def test_add_certificates_allowed_applications(
        allowed_apps, allow_all, disallow_all, expected_args, not_expected_args, cli_argument_group):
    KeychainArgument.ALLOWED_APPLICATIONS.register(cli_argument_group)
    keychain = Keychain(path=pathlib.Path('/tmp/keychain'))

    with mock.patch.object(keychain, 'execute') as mock_execute, \
            mock.patch('codemagic.tools.keychain.shutil') as mock_shutil:
        mock_shutil.which = lambda path: str(path)
        mock_execute.return_value = Mock(returncode=0, spec=CliProcess)
        keychain.add_certificates(
            [pathlib.Path('*.p12')],
            allowed_applications=list(map(pathlib.Path, allowed_apps)),
            allow_all_applications=allow_all,
            disallow_all_applications=disallow_all,
        )
        mock_call_args = mock_execute.call_args[0][0]

    for arg in expected_args:
        assert arg in mock_call_args
    for arg in not_expected_args:
        assert arg not in mock_call_args


@mock.patch.object(Keychain, 'find_paths', mock_find_paths)
def test_add_certificates_all_apps_allowed_and_disallowed(cli_argument_group):
    KeychainArgument.ALLOW_ALL_APPLICATIONS.register(cli_argument_group)
    KeychainArgument.DISALLOW_ALL_APPLICATIONS.register(cli_argument_group)
    with pytest.raises(argparse.ArgumentError) as argument_error:
        Keychain(path=pathlib.Path('/tmp/keychain')).add_certificates(
            [pathlib.Path('*.p12')],
            allowed_applications=[],
            allow_all_applications=True,
            disallow_all_applications=True,
        )
    assert KeychainArgument.ALLOW_ALL_APPLICATIONS.flag in argument_error.value.argument_name
    assert 'mutually exclusive options' in argument_error.value.message
