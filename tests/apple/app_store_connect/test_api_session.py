from unittest import mock

import pytest
from requests import Response
from requests import Session

from codemagic.apple import AppStoreConnectApiError
from codemagic.apple.app_store_connect import AppStoreConnectApiSession


def _get_failed_response_mock(payload: dict, status_code: int):
    return mock.create_autospec(
        Response,
        instance=True,
        ok=False,
        status_code=status_code,
        json=mock.Mock(return_value=payload),
    )


@pytest.fixture
def mock_unauthorized_response():
    unauthorized_payload = {
        'errors': [
            {
                'status': '401',
                'code': 'NOT_AUTHORIZED',
                'title': 'Authentication credentials are missing or invalid.',
                'detail': (
                    'Provide a properly configured and signed bearer token, '
                    'and make sure that it has not expired. Learn more about '
                    'Generating Tokens for API Requests '
                    'https://developer.apple.com/go/?id=api-generating-tokens'
                ),
            },
        ],
    }
    return _get_failed_response_mock(unauthorized_payload, 401)


@pytest.fixture
def mock_server_error_response():
    server_error_payload = {
        'errors': [
            {
                'status': '500',
                'code': 'UNEXPECTED_ERROR',
                'title': 'An unexpected error occurred.',
                'detail': (
                    'An unexpected error occurred on the server side. '
                    'If this issue continues, contact us at '
                    'https://developer.apple.com/contact/.'
                ),
            },
        ],
    }
    return _get_failed_response_mock(server_error_payload, 500)


@pytest.fixture
def mock_not_found_response():
    not_found_payload = {
        'errors': [
            {
                'id': '143c2772-4b6c-4af5-8c21-45e4a993ffc8',
                'status': '404',
                'code': 'NOT_FOUND',
                'title': 'The specified resource does not exist',
                'detail': "There is no resource of type 'AppsV1' with id 'kana'",
            },
        ],
    }
    return _get_failed_response_mock(not_found_payload, 404)


@pytest.fixture
def mock_successful_response():
    return mock.create_autospec(Response, instance=True, ok=True, status_code=200)


@mock.patch.object(Session, 'request')
def test_unauthorized_retrying_success(mock_session, mock_successful_response, mock_unauthorized_response):
    mock_session.side_effect = (mock_unauthorized_response, mock_unauthorized_response, mock_successful_response)

    mock_auth_headers_factory = mock.Mock(return_value={})
    mock_revoke_auth_info = mock.Mock()
    session = AppStoreConnectApiSession(
        mock_auth_headers_factory,
        unauthorized_request_retries=3,
        revoke_auth_info=mock_revoke_auth_info,
    )
    final_response = session.get('https://example.com')

    # Check that only first call does not require JWT refresh
    assert mock_auth_headers_factory.mock_calls == [(), (), ()]
    assert mock_revoke_auth_info.mock_calls == [(), ()]
    mock_unauthorized_response.assert_not_called()
    mock_successful_response.assert_has_calls([('json', (), {})])

    # After unauthorized requests finally authentication passes and successful response is returned
    assert final_response is mock_successful_response


@mock.patch.object(Session, 'request')
def test_server_error_retrying_success(mock_session, mock_successful_response, mock_server_error_response):
    mock_session.side_effect = (mock_server_error_response, mock_server_error_response, mock_successful_response)

    mock_auth_headers_factory = mock.Mock(return_value={})
    mock_revoke_auth_info = mock.Mock()
    session = AppStoreConnectApiSession(
        mock_auth_headers_factory,
        server_error_retries=3,
        revoke_auth_info=mock_revoke_auth_info,
    )
    final_response = session.get('https://example.com')

    # Check that JWT refresh is not performed
    assert mock_auth_headers_factory.mock_calls == [(), (), ()]
    assert mock_revoke_auth_info.mock_calls == []
    mock_server_error_response.assert_not_called()
    mock_successful_response.assert_has_calls([('json', (), {})])

    # After unauthorized requests finally authentication passes and successful response is returned
    assert final_response is mock_successful_response


@mock.patch.object(Session, 'request')
def test_unauthorized_retrying_failure(mock_session, mock_unauthorized_response):
    retries_count = 3

    mock_session.side_effect = [mock_unauthorized_response for _ in range(retries_count + 1)]
    mock_auth_headers_factory = mock.Mock(return_value={})
    mock_revoke_auth_info = mock.Mock()
    session = AppStoreConnectApiSession(
        mock_auth_headers_factory,
        unauthorized_request_retries=retries_count,
        revoke_auth_info=mock_revoke_auth_info,
    )
    with pytest.raises(AppStoreConnectApiError) as error_info:
        session.get('https://example.com')

    assert session._unauthorized_retries == retries_count
    assert mock_session.call_count == retries_count

    # Check that only first call does not require JWT refresh
    assert mock_auth_headers_factory.mock_calls == [(), (), ()]
    assert mock_revoke_auth_info.mock_calls == [(), (), ()]

    # Finally when retries are exhausted the unauthorized error is still thrown
    assert error_info.value.response is mock_unauthorized_response


@mock.patch.object(Session, 'request')
def test_server_error_retrying_failure(mock_session, mock_server_error_response):
    retries_count = 3

    mock_session.side_effect = [mock_server_error_response for _ in range(retries_count + 1)]
    mock_auth_headers_factory = mock.Mock(return_value={})
    mock_revoke_auth_info = mock.Mock()
    session = AppStoreConnectApiSession(
        mock_auth_headers_factory,
        server_error_retries=retries_count,
        revoke_auth_info=mock_revoke_auth_info,
    )
    with pytest.raises(AppStoreConnectApiError) as error_info:
        session.get('https://example.com')

    assert session._server_error_retries == retries_count
    assert mock_session.call_count == retries_count

    # Check that JWT refresh is not performed
    assert mock_auth_headers_factory.mock_calls == [(), (), ()]
    assert mock_revoke_auth_info.mock_calls == []

    # Finally when retries are exhausted the unauthorized error is still thrown
    assert error_info.value.response is mock_server_error_response


@mock.patch.object(Session, 'request')
def test_http_error_not_found(mock_session, mock_successful_response, mock_not_found_response):
    mock_session.side_effect = (mock_not_found_response, mock_successful_response)

    mock_auth_headers_factory = mock.Mock(return_value={})
    mock_revoke_auth_info = mock.Mock()
    session = AppStoreConnectApiSession(
        mock_auth_headers_factory,
        unauthorized_request_retries=3,
        server_error_retries=3,
        revoke_auth_info=mock_revoke_auth_info,
    )
    with pytest.raises(AppStoreConnectApiError) as error_info:
        session.get('https://example.com')

    # Fail hard on first attempt on non-authorization error
    assert mock_session.call_count == 1

    mock_auth_headers_factory.assert_called_once()
    assert mock_auth_headers_factory.method_calls == []

    mock_revoke_auth_info.assert_not_called()
    mock_successful_response.assert_not_called()
    assert mock_successful_response.method_calls == []

    mock_not_found_response.assert_not_called()
    assert mock_not_found_response.method_calls == [('json', (), {}), ('json', (), {})]

    # Original error is raised
    assert error_info.value.response is mock_not_found_response
