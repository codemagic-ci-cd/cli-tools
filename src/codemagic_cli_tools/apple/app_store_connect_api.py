from __future__ import annotations

import enum
import logging
from datetime import datetime
from datetime import timedelta
from typing import Dict
from typing import List
from typing import NewType
from typing import Optional
from typing import Union

import jwt
import requests

from .resources import App
from .resources import BundleId
from .resources import BundleIdCapability
from .resources import BundleIdPlatform
from .resources import CapabilitySetting
from .resources import CapabilityType
from .resources import Certificate
from .resources import CertificateType
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


class CertificateOrdering(Ordering):
    CERTIFICATE_TYPE = 'certificateType'
    DISPLAY_NAME = 'displayName'
    ID = 'id'
    SERIAL_NUMBER = 'serialNumber'


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
        :param issuer_id: Your issuer ID from the API Keys page in App Store Connect (Ex: 57246542-96fe-1a63-e053-0824d011072a)
        :param private_key: Private key associated with the key_identifier you specified.
        """
        self._key_identifier = key_identifier
        self._issuer_id = issuer_id
        self._private_key = private_key
        self._jwt: Optional[str] = None
        self._jwt_expires: datetime = datetime.now()
        self._session = AppStoreConnectApiSession(self)
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

    def _paginate(self, url, params=None, page_size: Optional[int] = 100) -> List[Dict]:
        params = {k: v for k, v in (params or {}).items() if v is not None}
        if page_size is None:
            response = self._session.get(url, params=params).json()
        else:
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
                            attributes: Dict) -> Dict:
        return {
            'data': {
                'id': resource_id,
                'type': resource_type.value,
                'attributes': attributes
            }
        }

    @classmethod
    def _get_create_payload(cls,
                            resource_type: ResourceType, *,
                            attributes: Optional[Dict] = None,
                            relationships: Optional[Dict] = None) -> Dict:
        data = {'type': resource_type.value}
        if attributes is not None:
            data['attributes'] = attributes
        if relationships is not None:
            data['relationships'] = relationships
        return {'data': data}

    # ---------------------------------------------------------------------------- #
    # App operations                                                               #
    # https://developer.apple.com/documentation/appstoreconnectapi/testflight/apps #
    # ---------------------------------------------------------------------------- #

    def list_apps(self, ordering=AppOrdering.NAME, reverse=False) -> List[App]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_apps
        """
        apps = self._paginate(
            f'{self.API_URL}/apps',
            params={'sort': ordering.as_param(reverse)}
        )
        return [App(app) for app in apps]

    # ----------------------------------------------------------------------- #
    # Bundle ID operations                                                    #
    # https://developer.apple.com/documentation/appstoreconnectapi/bundle_ids #
    # ----------------------------------------------------------------------- #

    def register_bundle_id(self,
                           identifier: str,
                           name: str,
                           platform: BundleIdPlatform,
                           seed_id: Optional[str] = None) -> BundleId:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/register_a_new_bundle_id
        """
        attributes = {
            'name': name,
            'identifier': identifier,
            'platform': platform.value,
        }
        if seed_id:
            attributes['seedId'] = seed_id
        response = self._session.post(
            f'{self.API_URL}/bundleIds',
            json=self._get_create_payload(ResourceType.BUNDLE_ID, attributes=attributes)
        ).json()
        return BundleId(response['data'])

    def modify_bundle_id(self, resource: Union[LinkedResourceData, ResourceId], name: str) -> BundleId:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/modify_a_bundle_id
        """
        if isinstance(resource, LinkedResourceData):
            resource_id = resource.id
        else:
            resource_id = resource
        payload = self._get_update_payload(resource_id, ResourceType.BUNDLE_ID, {'name': name})
        response = self._session.patch(f'{self.API_URL}/bundleIds/{resource_id}', json=payload).json()
        return BundleId(response['data'])

    def delete_bundle_id(self, resource: Union[LinkedResourceData, ResourceId]) -> None:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/delete_a_bundle_id
        """
        if isinstance(resource, LinkedResourceData):
            resource_id = resource.id
        else:
            resource_id = resource
        self._session.delete(f'{self.API_URL}/bundleIds/{resource_id}')

    def list_bundle_ids(self, ordering=BundleIdOrdering.NAME, reverse=False) -> List[BundleId]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_bundle_ids
        """
        bundle_ids = self._paginate(f'{self.API_URL}/bundleIds', params={'sort': ordering.as_param(reverse)})
        return [BundleId(bundle_id) for bundle_id in bundle_ids]

    def read_bundle_id(self, resource: Union[LinkedResourceData, ResourceId]) -> BundleId:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/read_bundle_id_information
        """
        if isinstance(resource, LinkedResourceData):
            resource_id = resource.id
        else:
            resource_id = resource
        response = self._session.get(f'{self.API_URL}/bundleIds/{resource_id}').json()
        return BundleId(response['data'])

    def list_bundle_id_profile_ids(self, resource: Union[BundleId, ResourceId]) -> List[LinkedResourceData]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/get_all_profile_ids_for_a_bundle_id
        """
        if isinstance(resource, BundleId):
            url = resource.relationships.profiles.links.itself
        else:
            url = f'{self.API_URL}/bundleIds/{resource}/relationships/profiles'
        return [LinkedResourceData(bundle_id_profile) for bundle_id_profile in self._paginate(url)]

    def list_bundle_id_profiles(self, resource: Union[BundleId, ResourceId]) -> List[Profile]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_all_profiles_for_a_bundle_id
        """
        if isinstance(resource, BundleId):
            url = resource.relationships.profiles.links.related
        else:
            url = f'{self.API_URL}/bundleIds/{resource}/profiles'
        return [Profile(profile) for profile in self._paginate(url)]

    def list_bundle_id_capabilility_ids(self, resource: Union[BundleId, ResourceId]) -> List[LinkedResourceData]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/get_all_capabilility_ids_for_a_bundle_id
        """
        if isinstance(resource, BundleId):
            url = resource.relationships.bundleIdCapabilities.links.itself
        else:
            url = f'{self.API_URL}/bundleIds/{resource}/relationships/bundleIdCapabilities'
        return [LinkedResourceData(capabilility) for capabilility in self._paginate(url, page_size=None)]

    def list_bundle_id_capabilities(self, resource: Union[BundleId, ResourceId]) -> List[BundleIdCapability]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_all_capabilities_for_a_bundle_id
        """
        if isinstance(resource, BundleId):
            url = resource.relationships.bundleIdCapabilities.links.related
        else:
            url = f'{self.API_URL}/bundleIds/{resource}/bundleIdCapabilities'
        return [BundleIdCapability(capabilility) for capabilility in self._paginate(url, page_size=None)]

    # ----------------------------------------------------------------------------------- #
    # Bundle ID Capabilities operations                                                   #
    # https://developer.apple.com/documentation/appstoreconnectapi/bundle_id_capabilities #
    # ----------------------------------------------------------------------------------- #

    def enable_capability(self,
                          capability_type: CapabilityType,
                          bundle_id_resource: Union[ResourceId, BundleId],
                          capability_settings: Optional[CapabilitySetting] = None) -> BundleIdCapability:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/enable_a_capability
        """
        if isinstance(bundle_id_resource, BundleId):
            bundle_id = bundle_id_resource.id
        else:
            bundle_id = bundle_id_resource

        attributes = {'capabilityType': capability_type.value}
        if capability_settings is not None:
            attributes['settings'] = capability_settings.dict()
        relationships = {
            'bundleId': {
                'data': {'id': bundle_id, 'type': ResourceType.BUNDLE_ID.value}
            }
        }
        payload = self._get_create_payload(
            ResourceType.BUNDLE_ID_CAPABILITIES, attributes=attributes, relationships=relationships)
        response = self._session.post(f'{self.API_URL}/bundleIdCapabilities', json=payload).json()
        return BundleIdCapability(response['data'])

    def disable_capability(self, resource: Union[LinkedResourceData, ResourceId]) -> None:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/disable_a_capability
        """
        if isinstance(resource, LinkedResourceData):
            resource_id = resource.id
        else:
            resource_id = resource
        self._session.delete(f'{self.API_URL}/bundleIdCapabilities/{resource_id}')

    def modify_capability_configuration(self,
                                        resource: Union[LinkedResourceData, ResourceId],
                                        capability_type: CapabilityType,
                                        settings: Optional[CapabilitySetting]) -> BundleIdCapability:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/modify_a_capability_configuration
        """
        if isinstance(resource, LinkedResourceData):
            resource_id = resource.id
        else:
            resource_id = resource
        attributes = {'capabilityType': capability_type.value}
        if settings:
            attributes['settings'] = settings.dict()
        payload = self._get_update_payload(resource_id, ResourceType.BUNDLE_ID_CAPABILITIES, attributes=attributes)
        response = self._session.patch(f'{self.API_URL}/bundleIdCapabilities/{resource_id}', json=payload).json()
        return BundleIdCapability(response['data'])

    # ------------------------------------------------------------------------- #
    # Certificates operations                                                   #
    # https://developer.apple.com/documentation/appstoreconnectapi/certificates #
    # ------------------------------------------------------------------------- #

    def create_certificate(self):
        """
        https://developer.apple.com/documentation/appstoreconnectapi/create_a_certificate
        """

    def list_certificates(self,
                          filter_certificate_type: Optional[CertificateType] = None,
                          filter_display_name: Optional[str] = None,
                          ordering=CertificateOrdering.DISPLAY_NAME,
                          reverse=False) -> List[Certificate]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_and_download_certificates
        """
        params = {'sort': ordering.as_param(reverse)}
        if filter_certificate_type is not None:
            params['filter[certificateType]'] = filter_certificate_type.value
        if filter_display_name is not None:
            params['filter[displayName]'] = filter_display_name

        certificates = self._paginate(f'{self.API_URL}/certificates', params=params)
        return [Certificate(certificate) for certificate in certificates]

    def read_certificate(self):
        """
        https://developer.apple.com/documentation/appstoreconnectapi/read_and_download_certificate_information
        """

    def revoke_certificate(self):
        """
        https://developer.apple.com/documentation/appstoreconnectapi/revoke_a_certificate
        """


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
