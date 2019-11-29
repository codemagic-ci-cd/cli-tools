from __future__ import annotations

import logging
from datetime import datetime
from datetime import timedelta
from typing import Dict
from typing import List
from typing import NewType
from typing import Optional

import jwt

from .app_store_connect_api_session import AppStoreConnectApiSession
from .operations import AppOperations
from .operations import BundleIdCapabilitiesOperations
from .operations import BundleIdOperations
from .operations import CertificateOperations
from .operations import DeviceOperations
from .operations import ProfileOperations
from codemagic_cli_tools.apple.resources import ResourceId
from codemagic_cli_tools.apple.resources import ResourceType

KeyIdentifier = NewType('KeyIdentifier', str)
IssuerId = NewType('IssuerId', str)


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

    @property
    def devices(self) -> DeviceOperations:
        return DeviceOperations(self)

    @property
    def profiles(self) -> ProfileOperations:
        return ProfileOperations(self)
