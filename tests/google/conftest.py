import json
import os
from datetime import datetime
from datetime import timezone
from functools import lru_cache
from pathlib import Path
from unittest import mock

import pytest

from codemagic.google.resources import Release
from codemagic.google.resources import ReleaseNotes
from codemagic.google.resources.identifiers import AppIdentifier


@pytest.fixture
def release():
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
def release_response():
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
