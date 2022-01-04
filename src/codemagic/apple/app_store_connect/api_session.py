from __future__ import annotations

from typing import Callable
from typing import Dict

import requests

from codemagic.utilities import log

from .api_error import AppStoreConnectApiError


class AppStoreConnectApiSession(requests.Session):

    def __init__(
            self,
            auth_headers_factory: Callable[[], Dict[str, str]],
            log_requests: bool = False,
            unauthorized_request_retries: int = 1,
            revoke_auth_info: Callable[[], None] = lambda: None,
    ):
        super().__init__()
        self._auth_headers_factory = auth_headers_factory
        self._revoke_auth_info = revoke_auth_info
        self._logger = log.get_logger(self.__class__, log_to_stream=log_requests)
        self._unauthorized_retries = unauthorized_request_retries

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

    def request(self, *args, **kwargs) -> requests.Response:
        for attempt in range(1, self._unauthorized_retries+1):
            self._log_request(*args, **kwargs)
            headers = kwargs.pop('headers', {})
            if attempt > 1:
                self._revoke_auth_info()
            headers.update(self._auth_headers_factory())
            kwargs['headers'] = headers
            response = super().request(*args, **kwargs)
            self._log_response(response)

            if response.ok:
                return response
            elif response.status_code != 401:  # Not an authorization failure, fail immediately
                raise AppStoreConnectApiError(response)
            elif attempt == self._unauthorized_retries:
                self._logger.info('Unauthorized request retries are exhausted with %d attempts, stop trying', attempt)
                self._revoke_auth_info()
                raise AppStoreConnectApiError(response)
            else:
                self._logger.info('Request failed due to authentication failure on attempt #%d, try again', attempt)

        # Make mypy happy. We should never end up here.
        raise RuntimeError('Request attempts exhausted without raising or returning')
