import pathlib
import textwrap
from datetime import datetime
from datetime import timedelta
from unittest import mock
from unittest.mock import PropertyMock

import pytest

from codemagic.apple.app_store_connect import ApiKey
from codemagic.apple.app_store_connect import IssuerId
from codemagic.apple.app_store_connect import KeyIdentifier
from codemagic.apple.app_store_connect.json_web_token_manager import JWT
from codemagic.apple.app_store_connect.json_web_token_manager import JsonWebTokenManager


@pytest.fixture
def api_key() -> ApiKey:
    private_key = textwrap.dedent("""\
        -----BEGIN PRIVATE KEY-----
        MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQgjS1dn4LndSQZobdo
        XuOYMDM7IORFgYsqlkubi1IdggGgCgYIKoZIzj0DAQehRANCAARKFN3g9EbK7zqP
        cG0Wb1H2ig75cOb8IxFP6t91GOc4iG0vd2jWNyOgL0cBwDBILjjoLtVyX5S0XsTH
        eMRNMcL/
        -----END PRIVATE KEY-----
        """)
    return ApiKey(
        KeyIdentifier('0XCKGCB1A2'),
        IssuerId('0kqg3czj-03n5-q9b3-o2o6-vqlmht03xdy9'),
        private_key,
    )


@pytest.fixture
def sample_jwt(api_key) -> JWT:
    return JWT(
        key_id=api_key.identifier,
        token=(
            'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiIsImtpZCI6IjBYQ0tHQ0IxQTIifQ.'
            'eyJpc3MiOiIwa3FnM2N6ai0wM241LXE5YjMtbzJvNi12cWxtaHQwM3hkeTkiLCJ'
            'leHAiOjE2Mzk5OTU1NDAsImF1ZCI6ImFwcHN0b3JlY29ubmVjdC12MSJ9.qfZXO'
            'O1GSYdZR-3Is1O_KfBPyZglK3h0iCuj2GbCere3V9-5vObucmP72EZuyZBu92Mz'
            'yrFchDQEijQ6V5FIRA'
        ),
        payload={'iss': api_key.issuer_id, 'exp': 1639995540, 'aud': 'appstoreconnect-v1'},
        expires_at=datetime(2021, 12, 20, 12, 19),
    )


@mock.patch('codemagic.apple.app_store_connect.json_web_token_manager.jwt')
@mock.patch('codemagic.apple.app_store_connect.json_web_token_manager.datetime')
def test_load_from_file_cache(mock_datetime, mock_jwt, api_key, sample_jwt):
    mock_datetime.now.return_value = sample_jwt.expires_at - timedelta(minutes=10)
    mock_datetime.fromtimestamp.return_value = sample_jwt.expires_at
    mock_jwt.decode.return_value = sample_jwt.payload
    mock_cache_path = mock.Mock(spec=pathlib.Path, read_text=mock.Mock(return_value=sample_jwt.token))

    with mock.patch.object(JsonWebTokenManager, 'cache_path', new_callable=PropertyMock(return_value=mock_cache_path)):
        jwt = JsonWebTokenManager(api_key, enable_cache=True).get_jwt()

    # Check that correct JWT is loaded from cache
    assert jwt == sample_jwt
    mock_datetime.fromtimestamp.assert_called_with(sample_jwt.payload['exp'])

    # Check that cache file has only been read and not written
    assert len(mock_cache_path.method_calls) == 1
    mock_cache_path.read_text.assert_called()
    mock_cache_path.unlink.assert_not_called()
    mock_cache_path.write_text.assert_not_called()

    # Check that cached token is decoded and nothing is encoded
    mock_jwt.decode.assert_called()
    mock_jwt.encode.assert_not_called()


@mock.patch('codemagic.apple.app_store_connect.json_web_token_manager.jwt')
@mock.patch('codemagic.apple.app_store_connect.json_web_token_manager.datetime')
def test_disk_cache_is_disabled(mock_datetime, mock_jwt, api_key):
    now = datetime(2021, 12, 20, 12, 19)
    mock_datetime.now.return_value = now
    mock_jwt.encode.return_value = '<token>'
    mock_cache_path = mock.Mock(spec=pathlib.Path)

    with mock.patch.object(JsonWebTokenManager, 'cache_path', new_callable=PropertyMock(return_value=mock_cache_path)):
        jwt_manager = JsonWebTokenManager(api_key, token_duration=10*60, enable_cache=False)
        jwt = jwt_manager.get_jwt()

    expected_expires_at = now + timedelta(minutes=10)
    expected_payload = {
        'iss': api_key.issuer_id,
        'exp': expected_expires_at.timestamp(),
        'aud': 'appstoreconnect-v1',
    }

    # Check that expected JWT is generated
    assert jwt.token == '<token>'
    assert jwt.expires_at == expected_expires_at
    assert jwt.key_id == api_key.identifier
    assert jwt.payload == expected_payload

    mock_datetime.fromtimestamp.assert_not_called()

    # Check that cache file has not been interacted with
    mock_cache_path.assert_not_called()

    # Check that token is encoded and nothing is decoded from cache
    mock_jwt.decode.assert_not_called()
    mock_jwt.encode.assert_called()


@mock.patch('codemagic.apple.app_store_connect.json_web_token_manager.jwt')
@mock.patch('codemagic.apple.app_store_connect.json_web_token_manager.datetime')
def test_cache_expired(mock_datetime, mock_jwt, api_key, sample_jwt):
    now = sample_jwt.expires_at + timedelta(days=1)
    mock_datetime.now.return_value = now
    mock_datetime.fromtimestamp.return_value = sample_jwt.expires_at
    mock_jwt.decode.return_value = sample_jwt.payload
    mock_jwt.encode.return_value = '<token>'
    mock_cache_path = mock.Mock(spec=pathlib.Path, read_text=mock.Mock(return_value=sample_jwt.token))
    with mock.patch.object(JsonWebTokenManager, 'cache_path', new_callable=PropertyMock(return_value=mock_cache_path)):
        jwt = JsonWebTokenManager(api_key, token_duration=60*10, enable_cache=True).get_jwt()

    expected_expires_at = now + timedelta(minutes=10)
    expected_payload = {
        'iss': api_key.issuer_id,
        'exp': expected_expires_at.timestamp(),
        'aud': 'appstoreconnect-v1',
    }

    mock_jwt.decode.assert_called()  # Cached token should be decoded
    assert mock_jwt.decode.call_args[0][:2] == (sample_jwt.token, api_key.private_key)
    mock_jwt.encode.assert_called()  # New token must be encoded
    assert mock_jwt.encode.call_args[0][:2] == (expected_payload, api_key.private_key)

    mock_cache_path.read_text.assert_called()  # Cached token is read
    mock_cache_path.unlink.assert_called()  # Cache is revoked because of invalid token
    mock_cache_path.write_text.assert_called()  # New token must be cached

    assert jwt.token == '<token>'
    assert jwt.expires_at == expected_expires_at
    assert jwt.key_id == api_key.identifier
    assert jwt.payload == expected_payload


@mock.patch('codemagic.apple.app_store_connect.json_web_token_manager.jwt')
@mock.patch('codemagic.apple.app_store_connect.json_web_token_manager.datetime')
def test_cache_not_found(mock_datetime, mock_jwt, api_key, sample_jwt):
    mock_datetime.now.return_value = datetime(2021, 12, 20, 12, 10, 0, 0)
    mock_jwt.encode.return_value = sample_jwt.token
    mock_cache_path = mock.Mock(spec=pathlib.Path, read_text=mock.Mock(side_effect=FileNotFoundError))
    with mock.patch.object(JsonWebTokenManager, 'cache_path', new_callable=PropertyMock(return_value=mock_cache_path)):
        jwt = JsonWebTokenManager(api_key, token_duration=60*10, enable_cache=True).get_jwt()

    mock_cache_path.read_text.assert_called()  # There should be an attempt to read from cache
    mock_cache_path.write_text.assert_called()  # New token should be written to cache

    # Check that cached token is decoded and nothing is encoded
    mock_jwt.encode.assert_called()
    mock_jwt.decode.assert_not_called()

    # Check that correct JWT is generated
    assert jwt.token == sample_jwt.token
    assert jwt.expires_at == datetime(2021, 12, 20, 12, 10+10, 0, 0)
    assert jwt.key_id == api_key.identifier


@mock.patch('codemagic.apple.app_store_connect.json_web_token_manager.jwt')
@mock.patch('codemagic.apple.app_store_connect.json_web_token_manager.datetime')
def test_token_expiration(mock_datetime, mock_jwt, api_key, sample_jwt):
    now = sample_jwt.expires_at + timedelta(days=1)
    mock_datetime.now.return_value = now
    mock_cache_path = mock.Mock(spec=pathlib.Path, read_text=mock.Mock(side_effect=FileNotFoundError))
    mock_jwt.encode.return_value = '<token>'

    with mock.patch.object(JsonWebTokenManager, 'cache_path', new_callable=PropertyMock(return_value=mock_cache_path)):
        manager = JsonWebTokenManager(api_key, token_duration=60*10, enable_cache=True)
        manager._jwt = sample_jwt
        jwt = manager.get_jwt()

    expected_expires_at = now + timedelta(minutes=10)
    expected_payload = {
        'iss': api_key.issuer_id,
        'exp': expected_expires_at.timestamp(),
        'aud': 'appstoreconnect-v1',
    }

    mock_jwt.decode.assert_not_called()  # Cached token should be not decoded as cache is not available
    mock_jwt.encode.assert_called()  # New token must be encoded
    assert mock_jwt.encode.call_args[0][:2] == (expected_payload, api_key.private_key)

    mock_cache_path.read_text.assert_called()  # Cached token is read
    mock_cache_path.unlink.assert_not_called()  # Nothing to revoke since cache does not exist
    mock_cache_path.write_text.assert_called()  # New token must be cached

    assert jwt.token == '<token>'
    assert jwt.expires_at == expected_expires_at
    assert jwt.key_id == api_key.identifier
    assert jwt.payload == expected_payload


@pytest.mark.parametrize('expected_is_expired, time_difference', [
    (True, timedelta(days=-5)),
    (True, timedelta(hours=-1)),
    (True, timedelta(minutes=-15)),
    (True, timedelta(minutes=-1)),
    (True, timedelta(seconds=-31)),
    (True, timedelta(seconds=-29)),
    (True, timedelta(seconds=-15)),
    (True, timedelta(seconds=-1)),
    (False, timedelta(seconds=0)),
    (False, timedelta(seconds=1)),
    (False, timedelta(seconds=60)),
    (False, timedelta(minutes=15)),
    (False, timedelta(hours=20)),
    (False, timedelta(days=5)),
])
@mock.patch('codemagic.apple.app_store_connect.json_web_token_manager.datetime')
def test_is_expired(mock_datetime, expected_is_expired, time_difference, api_key):
    now = datetime(year=2019, month=8, day=20)
    mock_datetime.now.return_value = now
    expires_at = now + time_difference
    jwt_manager = JsonWebTokenManager(api_key, enable_cache=True)
    assert jwt_manager._is_expired(expires_at) is expected_is_expired
