import dataclasses
import uuid
from unittest import mock

import pytest

from codemagic.apple.resources import Build
from codemagic.apple.resources import ResourceType
from codemagic.tools.app_store_connect import AppStoreConnect


def _mock_echo(*_args, **_kwargs):
    pass


def _get_build(version) -> Build:
    attributes = {f.name: None for f in dataclasses.fields(Build.Attributes)}
    attributes['version'] = version
    return Build({
        'attributes': attributes,
        'id': str(uuid.uuid4()),
        'links': {'self': None},
        'type': ResourceType.BUILDS.value,
    })


@pytest.mark.parametrize('versions, expected_latest_build_number', [
    ([], None),
    (['1.0.1', '2', '0.1'], '2'),
    (['2.0', '2'], '2.0'),
    (['11', '13', '14', '15', '12'], '15'),
    (['13.0.1.2.3.4.5'], '13.0.1.2.3.4.5'),
])
@mock.patch.object(AppStoreConnect, 'echo', _mock_echo)
def test_get_latest_build_number(versions, expected_latest_build_number):
    builds = list(map(_get_build, versions))
    latest_build_number = AppStoreConnect._get_latest_build_number(builds)
    assert latest_build_number == expected_latest_build_number
