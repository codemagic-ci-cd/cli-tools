import dataclasses
from unittest import mock

import pytest

from codemagic.google.resources import Resource


@pytest.fixture
def mock_logger():
    mock_logger = mock.MagicMock()
    with mock.patch("codemagic.utilities.log.get_logger", return_value=mock_logger):
        yield mock_logger


def test_from_api_response(mock_logger: mock.MagicMock):
    @dataclasses.dataclass
    class MyGoogleResource(Resource):
        field: str

    resource = MyGoogleResource.from_api_response(
        {
            "field": "value",
            "undefined": 100,
        },
    )
    assert resource == MyGoogleResource(field="value")
    mock_logger.warning.assert_called_once_with("Unknown field %r for resource %s", "undefined", "MyGoogleResource")
