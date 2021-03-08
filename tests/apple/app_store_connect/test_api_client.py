from datetime import datetime
from datetime import timedelta
from datetime import timezone
from unittest import mock

import pytest

NOW = datetime(year=2019, month=8, day=20)
UTC_NOW = datetime(year=2019, month=8, day=20, tzinfo=timezone.utc)


@pytest.fixture
def freeze_now():
    with mock.patch('codemagic.apple.app_store_connect.api_client.datetime') as mock_now:
        mock_now.now.return_value = NOW
        mock_now.utcnow.return_value = UTC_NOW
        mock_now.side_effect = lambda *args, **kw: datetime(*args, **kw)
        yield


@pytest.mark.parametrize('is_expired, jwt_expires', [
    (True, NOW - timedelta(days=5)),
    (True, NOW - timedelta(hours=1)),
    (True, NOW - timedelta(minutes=15)),
    (True, NOW - timedelta(seconds=31)),
    (False, NOW),
    (False, NOW - timedelta(seconds=15)),
    (False, NOW - timedelta(seconds=29)),
    (False, NOW + timedelta(seconds=60)),
    (False, NOW + timedelta(minutes=15)),
    (False, NOW + timedelta(hours=20)),
    (False, NOW + timedelta(days=5)),
])
def test_is_token_expired(jwt_expires, is_expired, app_store_api_client, freeze_now):
    app_store_api_client._jwt_expires = jwt_expires
    assert app_store_api_client._is_token_expired() is is_expired


def test_auth_headers(app_store_api_client):
    assert app_store_api_client.jwt in app_store_api_client.generate_auth_headers()['Authorization']
