from __future__ import annotations

from typing import Callable
from typing import Dict

import requests

from codemagic.utilities import auditing
from codemagic.utilities import log

from .api_error import AppStoreConnectApiError


class AppStoreConnectApiSession(requests.Session):

    def __init__(
        self,
        auth_headers_factory: Callable[[], Dict[str, str]],
        log_requests: bool = False,
        unauthorized_request_retries: int = 1,
        server_error_retries: int = 1,
        revoke_auth_info: Callable[[], None] = lambda: None,
    ):
        super().__init__()
        self._auth_headers_factory = auth_headers_factory
        self._revoke_auth_info = revoke_auth_info
        self._logger = log.get_logger(self.__class__, log_to_stream=log_requests)
        self._unauthorized_retries = unauthorized_request_retries
        self._server_error_retries = server_error_retries

    def _log_response(self, response):
        try:
            self._logger.info(f'<<< {response.status_code} {response.json()}')
        except ValueError:
            self._logger.info(f'<<< {response.status_code} {response.content}')

    def _log_request(self, *args, **kwargs):
        method = args[0].upper()
        url = args[1]
        body = kwargs.get('params') or kwargs.get('data') or kwargs.get('json')
        if isinstance(body, dict):
            body = {k: (v if 'password' not in k.lower() else '*******') for k, v in body.items()}
        self._logger.info(f'>>> {method} {url} {body}')

    def _handle_unauthorized_request_response(self, attempt: int, response: requests.Response):
        self._revoke_auth_info()
        if attempt >= self._unauthorized_retries:
            self._logger.info(f'Unauthorized request retries are exhausted with {attempt} attempts, stop trying')
            raise AppStoreConnectApiError(response)

        self._logger.info(f'Request failed due to authentication failure on attempt #{attempt}, try again')

    def _handle_server_error_response(self, attempt: int, response: requests.Response):
        if attempt >= self._server_error_retries:
            self._logger.info(f'Server error retries are exhausted with {attempt} attempts, stop trying')
            raise AppStoreConnectApiError(response)

        self._logger.info(f'Request failed due to server error {response.status_code} on attempt #{attempt}, try again')

    def _do_request(
        self,
        *request_args,
        unauthorized_attempt: int = 1,
        server_error_attempt: int = 1,
        **request_kwargs,
    ) -> requests.Response:
        self._log_request(*request_args, **request_kwargs)
        headers = request_kwargs.pop('headers', {})
        headers.update(self._auth_headers_factory())
        request_kwargs['headers'] = headers
        response = super().request(*request_args, **request_kwargs)
        self._log_response(response)

        if response.ok:
            return response

        # Request failed, save request info and see if we can retry it
        auditing.save_http_request_audit(response, audit_directory_name='failed-http-requests')

        if response.status_code == 401:
            self._handle_unauthorized_request_response(unauthorized_attempt, response)
            unauthorized_attempt = unauthorized_attempt + 1
        elif response.status_code >= 500:
            self._handle_server_error_response(server_error_attempt, response)
            server_error_attempt = server_error_attempt + 1
        else:
            # Neither authorization failure nor server error, fail immediately
            raise AppStoreConnectApiError(response)

        return self._do_request(
            *request_args,
            unauthorized_attempt=unauthorized_attempt,
            server_error_attempt=server_error_attempt,
            **request_kwargs,
        )

    def request(self, *args, **kwargs) -> requests.Response:
        return self._do_request(*args, **kwargs)
