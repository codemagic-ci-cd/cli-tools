from __future__ import annotations

import argparse
import json
import os
import pathlib
from tempfile import NamedTemporaryFile
from typing import List
from unittest import mock

import pytest

from codemagic.google_play.resources import Track
from codemagic.tools.google_play import GooglePlay
from codemagic.tools.google_play.argument_types import CredentialsArgument
from codemagic.tools.google_play.arguments import GooglePlayArgument
from codemagic.tools.google_play.errors import GooglePlayError

credentials_argument = GooglePlayArgument.GCLOUD_SERVICE_ACCOUNT_CREDENTIALS


@pytest.fixture
def mock_tracks() -> List[Track]:
    mock_response_path = pathlib.Path(__file__).parent / 'mocks' / 'google_play_tracks.json'
    tracks_response = json.loads(mock_response_path.read_text())
    return [Track(**track) for track in tracks_response]


@pytest.fixture(autouse=True)
def register_args(cli_argument_group):
    for arg in GooglePlay.CLASS_ARGUMENTS:
        arg.register(cli_argument_group)


@pytest.fixture()
def namespace_kwargs():
    ns_kwargs = {
        credentials_argument.key: CredentialsArgument('{"type":"service_account"}'),
    }
    for arg in GooglePlay.CLASS_ARGUMENTS:
        if not hasattr(arg.type, 'environment_variable_key'):
            continue
        os.environ.pop(arg.type.environment_variable_key, None)
    return ns_kwargs


def test_missing_credentials_arg(namespace_kwargs):
    namespace_kwargs[credentials_argument.key] = None
    cli_args = argparse.Namespace(**dict(namespace_kwargs.items()))

    with pytest.raises(argparse.ArgumentError) as exception_info:
        GooglePlay.from_cli_args(cli_args)

    message = str(exception_info.value)
    assert credentials_argument.key.upper() in message
    if hasattr(credentials_argument.type, 'environment_variable_key'):
        assert credentials_argument.type.environment_variable_key in message
    assert ','.join(credentials_argument.flags) in message


def test_invalid_credentials_from_env(namespace_kwargs):
    os.environ[CredentialsArgument.environment_variable_key] = 'invalid credentials'
    namespace_kwargs[credentials_argument.key] = None
    cli_args = argparse.Namespace(**dict(namespace_kwargs.items()))
    with pytest.raises(argparse.ArgumentError) as exception_info:
        GooglePlay.from_cli_args(cli_args)
    assert str(exception_info.value) == 'argument --credentials: Provided value "invalid credentials" is not valid'


def test_credentials_invalid_path(namespace_kwargs):
    os.environ[CredentialsArgument.environment_variable_key] = '@file:this-is-not-a-file'
    namespace_kwargs[credentials_argument.key] = None
    cli_args = argparse.Namespace(**dict(namespace_kwargs.items()))
    with pytest.raises(argparse.ArgumentError) as exception_info:
        GooglePlay.from_cli_args(cli_args)
    assert str(exception_info.value) == 'argument --credentials: File "this-is-not-a-file" does not exist'


@mock.patch('codemagic.tools.google_play.google_play.GooglePlayDeveloperAPIClient')
def test_read_private_key(mock_google_play_api_client, namespace_kwargs):
    namespace_kwargs[credentials_argument.key] = CredentialsArgument('{"type":"service_account"}')
    _ = GooglePlay.from_cli_args(argparse.Namespace(**namespace_kwargs))
    mock_google_play_api_client.assert_called_once_with('{"type":"service_account"}')


@pytest.mark.parametrize('configure_variable', [
    lambda filename, ns_kwargs: os.environ.update(
        {credentials_argument.type.environment_variable_key: f'@file:{filename}'},
    ),
    lambda filename, ns_kwargs: ns_kwargs.update(
        {credentials_argument.key: CredentialsArgument(f'@file:{filename}')},
    ),
])
@mock.patch('codemagic.tools.google_play.google_play.GooglePlayDeveloperAPIClient')
def test_private_key_path_arg(mock_google_play_api_client, configure_variable, namespace_kwargs):
    with NamedTemporaryFile(mode='w') as tf:
        tf.write('{"type":"service_account"}')
        tf.flush()
        namespace_kwargs[credentials_argument.key] = None
        configure_variable(tf.name, namespace_kwargs)

        _ = GooglePlay.from_cli_args(argparse.Namespace(**namespace_kwargs))
        mock_google_play_api_client.assert_called_once_with('{"type":"service_account"}')


@pytest.mark.parametrize('configure_variable', [
    lambda ns_kwargs: os.environ.update(
        {credentials_argument.type.environment_variable_key: '@env:CREDENTIALS'},
    ),
    lambda ns_kwargs: ns_kwargs.update(
        {credentials_argument.key: CredentialsArgument('@env:CREDENTIALS')},
    ),
])
@mock.patch('codemagic.tools.google_play.google_play.GooglePlayDeveloperAPIClient')
def test_private_key_env_arg(mock_google_play_api_client, configure_variable, namespace_kwargs):
    os.environ['CREDENTIALS'] = '{"type":"service_account"}'
    namespace_kwargs[credentials_argument.key] = None
    configure_variable(namespace_kwargs)

    _ = GooglePlay.from_cli_args(argparse.Namespace(**namespace_kwargs))
    mock_google_play_api_client.assert_called_once_with('{"type":"service_account"}')


def test_get_track(mock_tracks):
    google_play = GooglePlay({'type': 'service_account'})
    mock_track = mock_tracks[0]
    with mock.patch.object(google_play.api_client, 'get_track', return_value=mock_track) as mock_get_track:
        track = google_play.get_track('com.example.app', mock_track.track)
        mock_get_track.assert_called_once_with('com.example.app', mock_track.track)
    assert track == mock_track


def test_list_tracks(mock_tracks):
    google_play = GooglePlay({'type': 'service_account'})
    with mock.patch.object(google_play.api_client, 'list_tracks', return_value=mock_tracks) as mock_list_tracks:
        tracks = google_play.list_tracks('com.example.app')
        mock_list_tracks.assert_called_once_with('com.example.app')
    assert tracks == mock_tracks


@pytest.mark.parametrize('tracks, expected_version_code', [
    ('alpha', 65),
    ('beta', 66),
    ('internal', 67),
    ((), 67),
    (('alpha', 'production'), 65),
    (('beta', 'production'), 66),
    (('internal', 'production'), 67),
    (('alpha', 'beta', 'internal'), 67),
    (('alpha', 'beta', 'internal', 'production'), 67),
])
def test_get_latest_build_number(tracks, expected_version_code, mock_tracks):
    tracks = (tracks,) if isinstance(tracks, str) else tracks
    google_play = GooglePlay({'type': 'service_account'})
    with mock.patch.object(google_play.api_client, 'list_tracks', return_value=mock_tracks) as mock_list_tracks:
        build_number = google_play.get_latest_build_number('com.example.app', tracks)
        mock_list_tracks.assert_called_once_with('com.example.app')
    assert build_number == expected_version_code


def test_get_latest_build_number_no_tracks():
    google_play = GooglePlay({'type': 'service_account'})
    with mock.patch.object(google_play.api_client, 'list_tracks', return_value=[]) as mock_list_tracks:
        with pytest.raises(GooglePlayError):
            google_play.get_latest_build_number('com.example.app')
        mock_list_tracks.assert_called_once_with('com.example.app')


@pytest.mark.parametrize('track_releases', [None, []])
def test_get_latest_build_number_no_releases(track_releases, mock_tracks):
    mock_track = mock_tracks[0]
    mock_track.releases = track_releases
    google_play = GooglePlay({'type': 'service_account'})
    with mock.patch.object(google_play.api_client, 'list_tracks', return_value=[mock_track]) as mock_list_tracks:
        with pytest.raises(GooglePlayError):
            google_play.get_latest_build_number('com.example.app')
        mock_list_tracks.assert_called_once_with('com.example.app')


@pytest.mark.parametrize('track_releases', [None, []])
def test_get_latest_build_number_no_version_codes(track_releases, mock_tracks):
    # Production track does not have releases with version code
    production_track = next(t for t in mock_tracks if t.track == 'production')
    google_play = GooglePlay({'type': 'service_account'})
    with mock.patch.object(google_play.api_client, 'list_tracks', return_value=[production_track]) as mock_list_tracks:
        with pytest.raises(GooglePlayError):
            google_play.get_latest_build_number('com.example.app')
        mock_list_tracks.assert_called_once_with('com.example.app')
