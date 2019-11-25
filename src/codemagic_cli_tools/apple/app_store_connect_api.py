import datetime
import logging
from typing import Dict, Optional, List, NewType

import jwt
import requests

try:
    from typing_extensions import Literal
except ImportError:
    Literal = tuple

KeyIdentifier = NewType('KeyIdentifier', str)
IssuerId = NewType('IssuerId', str)
AppsSortOptions = Literal['bundleId', '-bundleId', 'name', '-name', 'sku', '-sku']


class AppStoreConnectApi:
    JWT_AUDIENCE = 'appstoreconnect-v1'
    JWT_ALGORITHM = 'ES256'
    API_URL = 'https://api.appstoreconnect.apple.com/v1'

    def __init__(self, key_identifier: KeyIdentifier, issuer_id: IssuerId, private_key: str):
        """
        :param key_identifier: Your private key ID from App Store Connect (Ex: 2X9R4HXF34)
        :param issuer_id: Your issuer ID from the API Keys page in App Store Connect (Ex: 57246542-96fe-1a63-e053-0824d011072a)
        :param private_key: Private key associated with the key_identifier you specified.
        """
        self._key_identifier = key_identifier
        self._issuer_id = issuer_id
        self._private_key = private_key
        self._jwt: Optional[str] = None
        self._jwt_expires: datetime.datetime = datetime.datetime.now()
        self._session = AppStoreConnectApiSession(self)
        self._logger = logging.getLogger(self.__class__.__name__)

    @property
    def jwt(self):
        if self._jwt and not self._is_token_expired():
            return self._jwt
        payload = {
            'iss': self._issuer_id,
            'exp': self._get_timestamp(),
            'aud': AppStoreConnectApi.JWT_AUDIENCE
        }
        headers = {'kid': self._key_identifier}
        token = jwt.encode(payload, self._private_key, algorithm=AppStoreConnectApi.JWT_ALGORITHM, headers=headers)
        self._jwt = token.decode()
        return self._jwt

    def _is_token_expired(self) -> bool:
        delta = datetime.timedelta(seconds=30)
        return datetime.datetime.now() - delta > self._jwt_expires

    def _get_timestamp(self) -> int:
        now = datetime.datetime.now()
        delta = datetime.timedelta(minutes=19)
        dt = now + delta
        self._jwt_expires = dt
        return int(dt.timestamp())

    @property
    def auth_headers(self) -> Dict[str, str]:
        return {'Authorization': f'Bearer {self.jwt}'}

    def _paginate(self, url, params=None, page_size=100) -> List[Dict]:
        params = {k: v for k, v in (params or {}).items() if v is not None}
        payload = self._session.get(url, params={'limit': page_size, **params}).json()
        try:
            results = payload['data']
        except KeyError:
            results = []
        while 'next' in payload['links']:
            payload = self._session.get(payload['links']['next'], params=params).json()
            results.extend(payload['data'])
        return results

    def list_apps(self, sort: Optional[AppsSortOptions] = None) -> List:
        return self._paginate(
            f'{self.API_URL}/apps',
            params={'sort': sort}
        )


class AppStoreConnectApiSession(requests.Session):

    def __init__(self, app_store_connect_api: AppStoreConnectApi):
        super().__init__()
        self.api = app_store_connect_api
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
        headers.update(self.api.auth_headers)
        response = super().request(*args, **kwargs, headers=headers)
        self._log_response(response)
        return response
