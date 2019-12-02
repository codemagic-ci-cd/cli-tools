from __future__ import annotations

import logging
from typing import Callable, Dict

import requests

from .api_error import AppStoreConnectApiError


class AppStoreConnectApiSession(requests.Session):

    def __init__(self, auth_headers_factory: Callable[[], Dict[str, str]]):
        super().__init__()
        self._auth_headers_factory = auth_headers_factory
        self._logger = logging.getLogger(self.__class__.__name__)

    def _log_response(self, response):
        try:
            self._logger.info(f'<<< {response.status_code} {response.json()}')
        except ValueError:
            self._logger.info(f'<<< {response.status_code} {response.content}')

    def _log_request(self, *args, **kwargs):
        method = args[0].upper()
        url = args[1]
        body = kwargs.get('params') or kwargs.get('data')
        if isinstance(body, dict):
            body = {k: (v if 'password' not in k.lower() else '*******') for k, v in body.items()}
        self._logger.info(f'>>> {method} {url} {body}')

    def request(self, *args, **kwargs):
        self._log_request(*args, **kwargs)
        headers = kwargs.pop('headers', {})
        headers.update(self._auth_headers_factory())
        response = super().request(*args, **kwargs, headers=headers)
        self._log_response(response)
        if not response.ok:
            raise AppStoreConnectApiError(response)
        return response
