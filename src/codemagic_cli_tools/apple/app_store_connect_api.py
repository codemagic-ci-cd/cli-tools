import datetime
import enum
import logging
from typing import Dict, Optional, List, NewType, Union

import jwt
import requests

from .resources import App
from .resources import BundleId
from .resources import BundleIdPlatform
from .resources import ErrorResponse
from .resources import LinkedResourceData
from .resources import Profile
from .resources import ResourceId
from .resources import ResourceType

KeyIdentifier = NewType('KeyIdentifier', str)
IssuerId = NewType('IssuerId', str)


class Ordering(enum.Enum):
    def as_param(self, reverse=False):
        return f'{"-" if reverse else ""}{self.value}'


class AppOrdering(Ordering):
    BUNDLE_ID = 'bundleId'
    NAME = 'name'
    SKU = 'sku'


class BundleIdOrdering(Ordering):
    ID = 'id'
    NAME = 'name'
    PLATFORM = 'platform'
    SEED_ID = 'seedId'


class AppStoreConnectApiError(Exception):

    def __init__(self, response: requests.Response):
        self._response = response
        try:
            self.error_response = ErrorResponse(response.json())
        except ValueError:
            self.error_response = ErrorResponse.from_raw_response(response)

    @property
    def status_code(self):
        return self._response.status_code

    def __str__(self):
        return str(self.error_response)


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
        self._logger.debug('Generate new JWT for App Store Connect')
        token = jwt.encode(
            self._get_jwt_payload(),
            self._private_key,
            algorithm=AppStoreConnectApi.JWT_ALGORITHM,
            headers={'kid': self._key_identifier})
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

    def _get_jwt_payload(self):
        return {
            'iss': self._issuer_id,
            'exp': self._get_timestamp(),
            'aud': AppStoreConnectApi.JWT_AUDIENCE
        }

    @property
    def auth_headers(self) -> Dict[str, str]:
        return {'Authorization': f'Bearer {self.jwt}'}

    def _paginate(self, url, params=None, page_size=100) -> List[Dict]:
        params = {k: v for k, v in (params or {}).items() if v is not None}
        response = self._session.get(url, params={'limit': page_size, **params}).json()
        try:
            results = response['data']
        except KeyError:
            results = []
        while 'next' in response['links']:
            response = self._session.get(response['links']['next'], params=params).json()
            results.extend(response['data'])
        return results

    @classmethod
    def _get_update_payload(cls,
                            resource_id: ResourceId,
                            resource_type: ResourceType,
                            attributes: Dict):
        return {
            'data': {
                'id': resource_id,
                'type': resource_type.value,
                'attributes': attributes
            }
        }

    @classmethod
    def _get_create_payload(cls, resource_type: ResourceType, attributes: Dict):
        return {
            'data': {
                'type': resource_type.value,
                'attributes': attributes
            }
        }

    #####################################################
    # App operations
    #####################################################

    def list_apps(self, ordering=AppOrdering.NAME, reverse=False) -> List[App]:
        apps = self._paginate(
            f'{self.API_URL}/apps',
            params={'sort': ordering.as_param(reverse)}
        )
        return [App(app) for app in apps]

    #####################################################
    # Bundle ID operations
    #####################################################

    def register_bundle_id(self,
                           identifier: str,
                           name: str,
                           platform: BundleIdPlatform,
                           seed_id: Optional[str] = None) -> BundleId:
        attributes = {
            'name': name,
            'identifier': identifier,
            'platform': platform.value,
        }
        if seed_id:
            attributes['seedId'] = seed_id
        response = self._session.post(
            f'{self.API_URL}/bundleIds',
            json=self._get_create_payload(ResourceType.BUNDLE_ID, attributes)
        ).json()
        return BundleId(response['data'])

    def modify_bundle_id(self, resource_id: ResourceId, name: str) -> BundleId:
        response = self._session.patch(
            f'{self.API_URL}/bundleIds/{resource_id}',
            json=self._get_update_payload(resource_id, ResourceType.BUNDLE_ID, {'name': name})
        ).json()
        return BundleId(response['data'])

    def delete_bundle_id(self, resource_id: ResourceId):
        self._session.delete(f'{self.API_URL}/bundleIds/{resource_id}')

    def list_bundle_ids(self, ordering=BundleIdOrdering.NAME, reverse=False) -> List[BundleId]:
        bundle_ids = self._paginate(
            f'{self.API_URL}/bundleIds',
            params={'sort': ordering.as_param(reverse)}
        )
        return [BundleId(bundle_id) for bundle_id in bundle_ids]

    def read_bundle_id(self, resource_id: ResourceId) -> BundleId:
        response = self._session.get(f'{self.API_URL}/bundleIds/{resource_id}').json()
        return BundleId(response['data'])

    def list_bundle_id_profile_ids(
            self, resource: Union[BundleId, ResourceId]) -> List[LinkedResourceData]:
        if isinstance(resource, BundleId):
            url = resource.relationships.profiles.links.itself
        elif isinstance(resource, ResourceId):
            url = f'{self.API_URL}/bundleIds/{resource}/relationships/profiles'
        else:
            raise ValueError(f'Invalid resource for listing profiles: {resource}')
        return [LinkedResourceData(bundle_id_profile) for bundle_id_profile in self._paginate(url)]

    def list_bundle_id_profiles(
            self, resource: Union[BundleId, ResourceId]) -> List[Profile]:
        if isinstance(resource, BundleId):
            url = resource.relationships.profiles.links.related
        elif isinstance(resource, ResourceId):
            url = f'{self.API_URL}/bundleIds/{resource}/profiles'
        else:
            raise ValueError(f'Invalid resource for listing profiles: {resource}')
        return [Profile(profile) for profile in self._paginate(url)]


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
        if not response.ok:
            raise AppStoreConnectApiError(response)
        return response
