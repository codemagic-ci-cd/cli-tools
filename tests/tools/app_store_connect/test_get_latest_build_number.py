import dataclasses
import uuid
from typing import Tuple
from typing import Type
from typing import TypeVar
from unittest import mock

import pytest

from codemagic.apple.resources import Build
from codemagic.apple.resources import PreReleaseVersion
from codemagic.apple.resources import Resource
from codemagic.apple.resources import ResourceType
from codemagic.tools.app_store_connect import AppStoreConnect

R = TypeVar('R', bound=Resource)


@pytest.fixture
@mock.patch.object(AppStoreConnect, 'echo', lambda *_: None)
@mock.patch.object(AppStoreConnect, '_get_api_client', lambda _: None)
def app_store_connect() -> AppStoreConnect:
    return AppStoreConnect(None, None, None)


def _get_resource(version: str, resource_type: ResourceType, resource_class: Type[R]) -> R:
    return resource_class({
        'attributes': {
            **{f.name: None for f in dataclasses.fields(resource_class.Attributes)},
            'version': version,
        },
        'id': str(uuid.uuid4()),
        'links': {'self': None},
        'type': resource_type.value,
    })


def _get_version_and_build(versions: Tuple[str, str]) -> Tuple[PreReleaseVersion, Build]:
    version_name, build_number = versions

    pre_release_version = _get_resource(version_name, ResourceType.PRE_RELEASE_VERSIONS, PreReleaseVersion)
    build = _get_resource(build_number, ResourceType.BUILDS, Build)
    return pre_release_version, build


@pytest.mark.parametrize(
    'version_pairs, expected_latest_build_number', [
        (iter([]), None),
        ([('1.0', '12345')], '12345'),
        ([('1.2.3', '1.0.1'), ('1.2.3', '2'), ('1.2.3', '0.1')], '2'),
        ([('1.2.3', '2.0'), ('1.2.3', '2')], '2.0'),
        ([('1.0', '11'), ('1.0', '13'), ('1.0', '14'), ('1.0', '15'), ('1.0', '12')], '15'),
        ([('3.0', '13.0.1.2.3.4.5')], '13.0.1.2.3.4.5'),
        ([('3.0.9', '1'), ('3.0.9', '2'), ('3.0.8', '3')], '2'),
    ],
)
def test_get_latest_build_number(version_pairs, expected_latest_build_number, app_store_connect):
    versions_and_builds = map(_get_version_and_build, version_pairs)
    latest_build_number = app_store_connect._get_latest_build_number(versions_and_builds)
    assert latest_build_number == expected_latest_build_number
