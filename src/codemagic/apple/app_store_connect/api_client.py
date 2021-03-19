from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from typing import Dict
from typing import List
from typing import Optional
from urllib import parse

import jwt

from codemagic.mixins import StringConverterMixin
from codemagic.utilities import log

from .api_session import AppStoreConnectApiSession
from .builds import Builds
from .provisioning import BundleIdCapabilities
from .provisioning import BundleIds
from .provisioning import Devices
from .provisioning import Profiles
from .provisioning import SigningCertificates
from .versioning import AppStoreVersions
from .versioning import PreReleaseVersions


@dataclass
class PaginateResult:
    data: List[Dict]
    included: List[Dict]


class KeyIdentifier(str):
    pass


class IssuerId(str):
    pass


class AppStoreConnectApiClient(StringConverterMixin):
    JWT_AUDIENCE = 'appstoreconnect-v1'
    JWT_ALGORITHM = 'ES256'
    API_URL = 'https://api.appstoreconnect.apple.com/v1'
    API_KEYS_DOCS_URL = \
        'https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api'

    def __init__(self, key_identifier: KeyIdentifier, issuer_id: IssuerId, private_key: str, log_requests=False):
        """
        :param key_identifier: Your private key ID from App Store Connect (Ex: 2X9R4HXF34)
        :param issuer_id: Your issuer ID from the API Keys page in
                          App Store Connect (Ex: 57246542-96fe-1a63-e053-0824d011072a)
        :param private_key: Private key associated with the key_identifier you specified
        """
        self._key_identifier = key_identifier
        self._issuer_id = issuer_id
        self._private_key = private_key
        self._jwt: Optional[str] = None
        self._jwt_expires: datetime = datetime.now()
        self.session = AppStoreConnectApiSession(self.generate_auth_headers, log_requests=log_requests)
        self._logger = log.get_logger(self.__class__)

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
        self._jwt = self._str(token)
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
            'aud': AppStoreConnectApiClient.JWT_AUDIENCE,
        }

    def generate_auth_headers(self) -> Dict[str, str]:
        return {'Authorization': f'Bearer {self.jwt}'}

    def _paginate(self, url, params, page_size) -> PaginateResult:
        params = {k: v for k, v in (params or {}).items() if v is not None}
        if page_size is None:
            response = self.session.get(url, params=params).json()
        else:
            response = self.session.get(url, params={'limit': page_size, **params}).json()
        result = PaginateResult(response.get('data', []), response.get('included', []))
        while 'next' in response['links']:
            # Query params from previous pagination call can be included in the next URL
            # and duplicate parameters are not allowed, so we need to filter those out.
            parsed_url = parse.urlparse(response['links']['next'])
            included_params = parse.parse_qs(parsed_url.query)
            step_params = {k: v for k, v in params.items() if k not in included_params}
            response = self.session.get(response['links']['next'], params=step_params).json()
            result.data.extend(response['data'])
            result.included.extend(response.get('included', []))
        return result

    def paginate(self, url, params=None, page_size: Optional[int] = 100) -> List[Dict]:
        return self._paginate(url, params, page_size).data

    def paginate_with_included(self, url, params=None, page_size: Optional[int] = 100) -> PaginateResult:
        return self._paginate(url, params, page_size)

    @property
    def app_store_versions(self) -> AppStoreVersions:
        return AppStoreVersions(self)

    @property
    def builds(self) -> Builds:
        return Builds(self)

    @property
    def bundle_ids(self) -> BundleIds:
        return BundleIds(self)

    @property
    def bundle_id_capabilities(self) -> BundleIdCapabilities:
        return BundleIdCapabilities(self)

    @property
    def devices(self) -> Devices:
        return Devices(self)

    @property
    def pre_release_versions(self) -> PreReleaseVersions:
        return PreReleaseVersions(self)

    @property
    def profiles(self) -> Profiles:
        return Profiles(self)

    @property
    def signing_certificates(self) -> SigningCertificates:
        return SigningCertificates(self)
