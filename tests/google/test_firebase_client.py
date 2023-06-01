import json
import os
from functools import lru_cache
from pathlib import Path
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest

from codemagic.google import FirebaseClient
from codemagic.google.errors import GoogleCredentialsError
from codemagic.google.resource_managers import ReleaseManager
from codemagic.google.resources import OrderBy
from codemagic.google.resources import Release
from tests.google.stubs import google_request_pagination_stub
from tests.google.stubs import google_request_stub
from tests.google.stubs import google_resource_stub


def test_release(release_response, release):
    assert Release(**release_response) == release


@pytest.fixture
@lru_cache(1)
def credentials() -> dict:
    if 'TEST_FIREBASE_SERVICE_ACCOUNT_CREDENTIALS_PATH' in os.environ:
        credentials_path = Path(os.environ['TEST_FIREBASE_SERVICE_ACCOUNT_CREDENTIALS_PATH'])
        credentials = credentials_path.expanduser().read_text()
    elif 'TEST_FIREBASE_SERVICE_ACCOUNT_CREDENTIALS_CONTENT' in os.environ:
        credentials = os.environ['TEST_FIREBASE_SERVICE_ACCOUNT_CREDENTIALS_CONTENT']
    else:
        raise KeyError(
            'TEST_FIREBASE_SERVICE_ACCOUNT_CREDENTIALS_PATH',
            'TEST_FIREBASE_SERVICE_ACCOUNT_CREDENTIALS_CONTENT',
        )
    return json.loads(credentials)


@pytest.mark.parametrize(
    'credentials', [
        {},
        {'type': 'service_account'},
        {'type': 'service_account', 'client_email': 'user@example.com'},
        {
            'type': 'service_account', 'client_email': 'user@example.com', 'client_id': 'client-id',
            'private_key': 'invalid-private-key', 'private_key_id': 'private-key-id',
        },
    ],
)
def test_invalid_credentials(credentials, app_identifier):
    with pytest.raises(GoogleCredentialsError):
        FirebaseClient(credentials).releases.list(app_identifier)


@pytest.fixture
def firebase_client():
    with patch.object(FirebaseClient, 'google_resource', new_callable=PropertyMock) as mock_firebase_app_distribution:
        mock_firebase_app_distribution.return_value = None
        yield FirebaseClient({})


@pytest.fixture
def mock_releases(release_response):
    release_0 = release_response.copy()
    release_1 = release_response.copy()
    release_1['buildVersion'] = '71'
    with patch.object(ReleaseManager, '_releases', new_callable=PropertyMock) as mock_resource:
        request_stub = google_request_stub([release_0, release_1], 'releases')
        mock_resource.return_value = google_resource_stub(request_stub)
        yield mock_resource


def test_list_releases(app_identifier, firebase_client, release, mock_releases):
    order_by = OrderBy.CREATE_TIME_ASC
    releases = firebase_client.releases.list(app_identifier, order_by=order_by, page_size=2)

    assert releases[0] == release
    assert releases[1].buildVersion == 71


def test_list_releases_limit(app_identifier, firebase_client, mock_releases):
    releases = firebase_client.releases.list(app_identifier, limit=1)

    assert len(releases) == 1


@pytest.fixture
def mock_releases_pagination(release_response):
    release_0 = release_response.copy()
    release_1 = release_response.copy()
    release_1['buildVersion'] = '71'
    with patch.object(ReleaseManager, '_releases', new_callable=PropertyMock) as mock_resource:
        request_stub = google_request_pagination_stub([release_0, release_1], 'releases')
        mock_resource.return_value = google_resource_stub(request_stub)
        yield mock_resource


def test_list_releases_pagination(app_identifier, release, firebase_client, mock_releases_pagination):
    releases = firebase_client.releases.list(app_identifier, page_size=1)

    assert len(releases) == 2
    assert releases[0] == release
    assert releases[1].buildVersion == 71
