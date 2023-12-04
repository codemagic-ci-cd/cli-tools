from __future__ import annotations

from codemagic.apple.resources import ErrorResponse


def test_error_response_initialization(api_error_response):
    error_response = ErrorResponse(api_error_response)
    assert error_response.dict() == api_error_response


def test_error_response_with_links(api_error_response_with_links):
    error_response = ErrorResponse(api_error_response_with_links)
    assert error_response.dict() == api_error_response_with_links


def test_error_iter_associated_errors(api_error_response_entity_state_invalid):
    error_response = ErrorResponse(api_error_response_entity_state_invalid)
    associated_errors = list(error_response.iter_associated_errors())
    assert len(associated_errors) == 3
    assert associated_errors[0].source_pointer == "/data/attributes/description"
    assert associated_errors[1].source_pointer == "/data/attributes/keywords"
    assert associated_errors[2].source_pointer == "/data/attributes/supportUrl"
