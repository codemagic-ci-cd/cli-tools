from __future__ import annotations

from codemagic.apple.resources import ErrorResponse


def test_error_response_initialization(api_error_response):
    error_response = ErrorResponse(api_error_response)
    assert error_response.dict() == api_error_response


def test_error_response_with_links(api_error_response_with_links):
    error_response = ErrorResponse(api_error_response_with_links)
    assert error_response.dict() == api_error_response_with_links
