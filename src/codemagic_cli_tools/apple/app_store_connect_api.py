from __future__ import annotations

import logging
from datetime import datetime
from datetime import timedelta
from typing import Dict
from typing import List
from typing import NewType
from typing import Optional

import jwt
import requests

from apple.app_store_connect_operations import AppOperations
from apple.app_store_connect_operations import BundleIdCapabilitiesOperations
from apple.app_store_connect_operations import BundleIdOperations
from apple.app_store_connect_operations import CertificateOperations
from apple.resources import ErrorResponse
from apple.resources import ResourceId
from apple.resources import ResourceType

KeyIdentifier = NewType('KeyIdentifier', str)
IssuerId = NewType('IssuerId', str)


class AppStoreConnectApiError(Exception):

    def __init__(self, response: requests.Response):
        self.response = response
        try:
            self.error_response = ErrorResponse(response.json())
        except ValueError:
            self.error_response = ErrorResponse.from_raw_response(response)

    @property
    def request(self) -> requests.PreparedRequest:
        return self.response.request

    @property
    def status_code(self) -> int:
        return self.response.status_code

    def __str__(self):
        return f'{self.request.method} {self.request.url} returned {self.response.status_code}: {self.error_response}'


class AppStoreConnectApiClient:
    JWT_AUDIENCE = 'appstoreconnect-v1'
    JWT_ALGORITHM = 'ES256'
    API_URL = 'https://api.appstoreconnect.apple.com/v1'

    def __init__(self, key_identifier: KeyIdentifier, issuer_id: IssuerId, private_key: str):
        """
        :param key_identifier: Your private key ID from App Store Connect (Ex: 2X9R4HXF34)
        :param issuer_id: Your issuer ID from the API Keys page in
                          App Store Connect (Ex: 57246542-96fe-1a63-e053-0824d011072a)
        :param private_key: Private key associated with the key_identifier you specified.
        """
        self._key_identifier = key_identifier
        self._issuer_id = issuer_id
        self._private_key = private_key
        self._jwt: Optional[str] = None
        self._jwt_expires: datetime = datetime.now()
        self.session = AppStoreConnectApiSession(self)
        self._logger = logging.getLogger(self.__class__.__name__)

    @property
    def jwt(self) -> str:
        if self._jwt and not self._is_token_expired():
            return self._jwt
        self._logger.debug('Generate new JWT for App Store Connect')
        token = jwt.encode(
            self._get_jwt_payload(),
            self._private_key,
            algorithm=AppStoreConnectApiClient.JWT_ALGORITHM,
            headers={'kid': self._key_identifier})
        self._jwt = token.decode()
        return self._jwt

    def _is_token_expired(self) -> bool:
        delta = timedelta(seconds=30)
        return datetime.now() - delta > self._jwt_expires

    def _get_timestamp(self) -> int:
        now = datetime.now()
        delta = timedelta(minutes=19)
        dt = now + delta
        self._jwt_expires = dt
        return int(dt.timestamp())

    def _get_jwt_payload(self) -> Dict:
        return {
            'iss': self._issuer_id,
            'exp': self._get_timestamp(),
            'aud': AppStoreConnectApiClient.JWT_AUDIENCE
        }

    @property
    def auth_headers(self) -> Dict[str, str]:
        return {'Authorization': f'Bearer {self.jwt}'}

    def paginate(self, url, params=None, page_size: Optional[int] = 100) -> List[Dict]:
        params = {k: v for k, v in (params or {}).items() if v is not None}
        if page_size is None:
            response = self.session.get(url, params=params).json()
        else:
            response = self.session.get(url, params={'limit': page_size, **params}).json()
        try:
            results = response['data']
        except KeyError:
            results = []
        while 'next' in response['links']:
            response = self.session.get(response['links']['next'], params=params).json()
            results.extend(response['data'])
        return results

    @classmethod
    def get_update_payload(cls,
                           resource_id: ResourceId,
                           resource_type: ResourceType,
                           attributes: Dict) -> Dict:
        return {
            'data': {
                'id': resource_id,
                'type': resource_type.value,
                'attributes': attributes
            }
        }

    @classmethod
    def get_create_payload(cls,
                           resource_type: ResourceType, *,
                           attributes: Optional[Dict] = None,
                           relationships: Optional[Dict] = None) -> Dict:
        data = {'type': resource_type.value}
        if attributes is not None:
            data['attributes'] = attributes
        if relationships is not None:
            data['relationships'] = relationships
        return {'data': data}

    @property
    def apps(self) -> AppOperations:
        return AppOperations(self)

    @property
    def bundle_ids(self) -> BundleIdOperations:
        return BundleIdOperations(self)

    @property
    def bundle_id_capabilities(self) -> BundleIdCapabilitiesOperations:
        return BundleIdCapabilitiesOperations(self)

    @property
    def certificates(self) -> CertificateOperations:
        return CertificateOperations(self)


class AppStoreConnectApiSession(requests.Session):

    def __init__(self, app_store_connect_api: AppStoreConnectApiClient):
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
        if not response.ok:
            raise AppStoreConnectApiError(response)
        return response
