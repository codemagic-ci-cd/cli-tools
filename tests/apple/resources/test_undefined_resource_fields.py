from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Optional

from codemagic.apple.resources import Resource
from codemagic.apple.resources.resource import Relationship


class MockResource(Resource):
    attributes: Attributes
    relationships: Optional[Relationships] = None

    @dataclass
    class Attributes(Resource.Attributes):
        name: str

    @dataclass
    class Relationships(Resource.Relationships):
        parent: Relationship


def test_mock_resource(api_mock_resource):
    resource = MockResource(api_mock_resource)
    assert resource.dict() == api_mock_resource


def test_undefined_attribute(api_mock_resource):
    api_mock_resource_with_excess_attribute = copy.deepcopy(api_mock_resource)
    api_mock_resource_with_excess_attribute['attributes']['age'] = 27
    resource = MockResource(api_mock_resource_with_excess_attribute)
    assert resource.dict() == api_mock_resource


def test_undefined_relationship(api_mock_resource):
    api_mock_resource_with_excess_relationship = copy.deepcopy(api_mock_resource)
    api_mock_resource_with_excess_relationship['relationships']['job'] = {
        'data': {
            'type': 'mockResource',
            'id': 'F88J43FA9J',
        },
        'links': {
            'self': 'https://example.com/mock_resource/F88J43FA9J',
        },
    }
    resource = MockResource(api_mock_resource_with_excess_relationship)
    assert resource.dict() == api_mock_resource
