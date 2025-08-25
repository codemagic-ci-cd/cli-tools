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
        s: str

    resource = MyGoogleResource.from_api_response(
        {
            "s": "lorem ipsum dolor sit amet",
            "i": 100,
        },
    )
    assert resource == MyGoogleResource(s="lorem ipsum dolor sit amet")
    mock_logger.warning.assert_called_once_with("Unknown field %r for resource %s", "i", "MyGoogleResource")
