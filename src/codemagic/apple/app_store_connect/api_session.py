from __future__ import annotations

from typing import Callable
from typing import Dict
from typing import Optional
from typing import Tuple

import requests

from codemagic.utilities import log

from .api_error import AppStoreConnectApiError


class AppStoreConnectApiSession(requests.Session):

    def __init__(self, auth_headers_factory: Callable[[], Dict[str, str]], log_requests: bool = False):
        super().__init__()
        self._auth_headers_factory = auth_headers_factory
        self._logger = log.get_logger(self.__class__, log_to_stream=log_requests)
        self._cache: Dict[Tuple[str, Optional[Tuple]], requests.Response] = {}

    def clear_cache(self):
        self._cache = {}

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

    @classmethod
    def _get_cache_key(cls, url: str, params: Optional[Dict]) -> Tuple[str, Optional[Tuple]]:
        if params is None:
            return url, params
        return url, tuple(sorted(params.items()))

    def _get_response_from_cache(self, url: str, params: Optional[Dict]) -> requests.Response:
        self._logger.info(f'>>> Try to use cached response for GET {url} {params}')
        cache_key = self._get_cache_key(url, params)
        try:
            response = self._cache[cache_key]
        except KeyError:
            self._logger.info(f'Cached response not found for GET {url}')
            raise
        else:
            self._logger.info(f'<<< Using cached response for GET {url}')
            return response

    def _cache_response(self, url: str, params: Optional[Dict], response: requests.Response) -> requests.Response:
        self._logger.info(f'<<< Cache response for GET {url} {params}')
        cache_key = self._get_cache_key(url, params)
        self._cache[cache_key] = response
        return response

    def get(self, url, use_cache: bool = False, **kwargs):
        params = kwargs.get('params')
        if use_cache:
            try:
                return self._get_response_from_cache(url, params)
            except KeyError:
                pass

        response = super().get(url, **kwargs)
        return self._cache_response(url, params, response)

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
