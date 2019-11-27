from datetime import datetime
from datetime import timedelta
from datetime import timezone
from unittest import mock

import pytest

FREEZED_NOW = datetime(year=2019, month=8, day=20)
FREEZED_UTC_NOW = datetime(year=2019, month=8, day=20, tzinfo=timezone.utc)


@pytest.fixture(autouse=False)
def freeze_now():
    with mock.patch('apple.app_store_connect_api.datetime') as mock_now:
        mock_now.now.return_value = FREEZED_NOW
        mock_now.utcnow.return_value = FREEZED_UTC_NOW
        mock_now.side_effect = lambda *args, **kw: datetime(*args, **kw)
        yield


@pytest.mark.parametrize('is_expired, jwt_expires', [
    (True, FREEZED_NOW - timedelta(days=5)),
    (True, FREEZED_NOW - timedelta(hours=1)),
    (True, FREEZED_NOW - timedelta(minutes=15)),
    (True, FREEZED_NOW - timedelta(seconds=31)),
    (False, FREEZED_NOW),
    (False, FREEZED_NOW - timedelta(seconds=15)),
    (False, FREEZED_NOW - timedelta(seconds=29)),
    (False, FREEZED_NOW + timedelta(seconds=60)),
    (False, FREEZED_NOW + timedelta(minutes=15)),
    (False, FREEZED_NOW + timedelta(hours=20)),
    (False, FREEZED_NOW + timedelta(days=5)),
])
def test_is_token_expired(jwt_expires, is_expired, api_client, freeze_now):
    api_client._jwt_expires = jwt_expires
    assert api_client._is_token_expired() is is_expired


def test_auth_headers(api_client):
    assert api_client.jwt in api_client.auth_headers['Authorization']
