from __future__ import annotations

from codemagic_cli_tools.apple.resources import ErrorResponse


def test_error_response_initialization(api_error_response):
    error_response = ErrorResponse(api_error_response)
    assert error_response.dict() == api_error_response
