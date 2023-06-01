import json
import os
from datetime import datetime
from datetime import timezone
from functools import lru_cache
from pathlib import Path
from unittest import mock
from unittest.mock import Mock
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest

from codemagic.google import FirebaseClient
from codemagic.google.errors import GoogleCredentialsError
from codemagic.google.resource_managers import ReleaseManager
from codemagic.google.resources import OrderBy
from codemagic.google.resources import Release
from codemagic.google.resources import ReleaseNotes
from codemagic.google.resources.identifiers import AppIdentifier


@pytest.fixture
def mock_release_response_data():
    return {
        'name': 'projects/228333310124/apps/1:228333310124:ios:5e439e0d0231a788ac8f09/releases/0fam13pr3rea0',
        'releaseNotes': {'text': 'Something new :) :)'},
        'displayVersion': '0.0.42',
        'buildVersion': '70',
        'createTime': '2023-05-18T12:30:17.454581Z',
        'firebaseConsoleUri': '',
        'testingUri': '',
        'binaryDownloadUri': '',
    }


@pytest.fixture
def mock_release():
    return Release(
        name='projects/228333310124/apps/1:228333310124:ios:5e439e0d0231a788ac8f09/releases/0fam13pr3rea0',
        releaseNotes=ReleaseNotes('Something new :) :)'),
        displayVersion='0.0.42',
        buildVersion=70,
        createTime=datetime(2023, 5, 18, 12, 30, 17, 454581, tzinfo=timezone.utc),
        firebaseConsoleUri=mock.ANY,
        testingUri=mock.ANY,
        binaryDownloadUri=mock.ANY,
    )


@pytest.fixture
def app_identifier():
    return AppIdentifier('228333310124', '1:228333310124:ios:5e439e0d0231a788ac8f09')


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


@pytest.fixture
def client(credentials):
    return FirebaseClient(credentials)


def test_release(mock_release_response_data, mock_release):
    assert Release(**mock_release_response_data) == mock_release


@pytest.mark.skipif(not os.environ.get('RUN_LIVE_API_TESTS'), reason='Live Firebase access')
def test_list_releases_live(app_identifier, credentials, client, mock_release):
    order_by = OrderBy.CREATE_TIME_ASC
    releases = client.releases.list(app_identifier, order_by=order_by, page_size=2)

    assert releases[0] == mock_release
    assert releases[1].buildVersion == 71


@pytest.mark.skipif(not os.environ.get('RUN_LIVE_API_TESTS'), reason='Live Firebase access')
def test_list_releases_pagination_live(app_identifier, credentials, client, mock_release):
    releases = client.releases.list(app_identifier, page_size=1)

    assert releases[0].buildVersion == 71
    assert releases[1] == mock_release


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
def mock_client():
    with patch.object(
        FirebaseClient,
        'service_resource',
        new_callable=PropertyMock,
    ) as mock_firebase_app_distribution:
        mock_firebase_app_distribution.return_value = None
        yield FirebaseClient({})


def google_request_stub(resources, resource_type_label):
    mock_execute = Mock()
    mock_execute.return_value = {resource_type_label: resources}

    class GoogleRequest:
        execute = mock_execute

    return GoogleRequest


def google_resource_stub(request_stub):
    class GoogleResource:
        @staticmethod
        def list(**_kw):
            return request_stub()

    return GoogleResource


@pytest.fixture
def mock_releases(mock_release_response_data):
    release_0 = mock_release_response_data.copy()
    release_1 = mock_release_response_data.copy()
    release_1['buildVersion'] = '71'
    with patch.object(ReleaseManager, '_releases', new_callable=PropertyMock) as mock_resource:
        request_stub = google_request_stub([release_0, release_1], 'releases')
        mock_resource.return_value = google_resource_stub(request_stub)
        yield mock_resource


def test_list_releases(app_identifier, mock_client, mock_release, mock_releases):
    order_by = OrderBy.CREATE_TIME_ASC
    releases = mock_client.releases.list(app_identifier, order_by=order_by, page_size=2)

    assert releases[0] == mock_release
    assert releases[1].buildVersion == 71


def test_list_releases_limit(app_identifier, mock_client, mock_releases):
    releases = mock_client.releases.list(app_identifier, limit=1)

    assert len(releases) == 1


def google_request_stub_pagination(resources, resource_type_label):
    mock_execute = Mock()
    mock_execute.side_effect = [
        {resource_type_label: [resources[0]], 'nextPageToken': 'next-page-token'},
        {resource_type_label: [resources[1]]},
    ]

    class GoogleRequest:
        execute = mock_execute

    return GoogleRequest


@pytest.fixture
def mock_releases_pagination(mock_release_response_data):
    release_0 = mock_release_response_data.copy()
    release_1 = mock_release_response_data.copy()
    release_1['buildVersion'] = '71'
    with patch.object(ReleaseManager, '_releases', new_callable=PropertyMock) as mock_resource:
        request_stub = google_request_stub_pagination([release_0, release_1], 'releases')
        mock_resource.return_value = google_resource_stub(request_stub)
        yield mock_resource


def test_list_releases_pagination(app_identifier, mock_release, mock_client, mock_releases_pagination):
    releases = mock_client.releases.list(app_identifier, page_size=1)

    assert len(releases) == 2
    assert releases[0] == mock_release
    assert releases[1].buildVersion == 71
