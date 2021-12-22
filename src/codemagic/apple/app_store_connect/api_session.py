from __future__ import annotations

from typing import Callable
from typing import Dict

import requests

from codemagic.utilities import log

from .api_error import AppStoreConnectApiError


class AppStoreConnectApiSession(requests.Session):

    def __init__(self, auth_headers_factory: Callable[[], Dict[str, str]], log_requests: bool = False):
        super().__init__()
        self._auth_headers_factory = auth_headers_factory
        self._logger = log.get_logger(self.__class__, log_to_stream=log_requests)

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
        self._log_request(*args, **kwargs)
        headers = kwargs.pop('headers', {})
        headers.update(self._auth_headers_factory())
        kwargs['headers'] = headers
        response = super().request(*args, **kwargs)
        self._log_response(response)
        if not response.ok:
            raise AppStoreConnectApiError(response)
        return response
