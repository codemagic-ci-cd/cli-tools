from __future__ import annotations

from typing import Dict
from typing import List
from typing import Optional
from urllib import parse

from codemagic.utilities import log

from .api_session import AppStoreConnectApiSession
from .apps import Apps
from .builds import Builds
from .json_web_token_manager import JsonWebTokenManager
from .provisioning import BundleIdCapabilities
from .provisioning import BundleIds
from .provisioning import Devices
from .provisioning import Profiles
from .provisioning import SigningCertificates
from .testflight import BetaGroups
from .type_declarations import ApiKey
from .type_declarations import IssuerId
from .type_declarations import KeyIdentifier
from .type_declarations import PaginateResult
from .versioning import AppStoreVersionLocalizations
from .versioning import AppStoreVersions
from .versioning import AppStoreVersionSubmissions
from .versioning import BetaAppReviewSubmissions
from .versioning import BetaBuildLocalizations
from .versioning import PreReleaseVersions
from .versioning import ReviewSubmissionItems
from .versioning import ReviewSubmissions


class AppStoreConnectApiClient:
    API_URL = 'https://api.appstoreconnect.apple.com/v1'
    API_KEYS_DOCS_URL = \
        'https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api'

    def __init__(
            self,
            key_identifier: KeyIdentifier,
            issuer_id: IssuerId,
            private_key: str,
            log_requests: bool = False,
            unauthorized_request_retries: int = 1,
            server_error_retries: int = 1,
            enable_jwt_cache: bool = False,
    ):
        """
        :param key_identifier: Your private key ID from App Store Connect (Ex: 2X9R4HXF34)
        :param issuer_id: Your issuer ID from the API Keys page in
                          App Store Connect (Ex: 57246542-96fe-1a63-e053-0824d011072a)
        :param private_key: Private key associated with the key_identifier you specified
        :param log_requests: Whether or not to log App Store Connect API requests and responses to STDOUT
        :param enable_jwt_cache: Whether or not to allow loading and writing generated App Store Connect
                                 JSON Web Token from or to a file cache.
        """
        self._logger = log.get_logger(self.__class__)
        self._api_key = ApiKey(key_identifier, issuer_id, private_key)
        self._jwt_manager = JsonWebTokenManager(self._api_key, enable_cache=enable_jwt_cache)
        self.session = AppStoreConnectApiSession(
            self.generate_auth_headers,
            log_requests=log_requests,
            unauthorized_request_retries=unauthorized_request_retries,
            server_error_retries=server_error_retries,
            revoke_auth_info=self._jwt_manager.revoke,
        )

    @property
    def jwt(self) -> str:
        jwt = self._jwt_manager.get_jwt()
        return jwt.token

    def generate_auth_headers(self) -> Dict[str, str]:
        return {'Authorization': f'Bearer {self.jwt}'}

    @classmethod
    def _get_pagination_page_size(cls, page_size: Optional[int], limit: Optional[int]) -> Optional[int]:
        if page_size is not None and limit is not None:
            return min(page_size, limit)
        return page_size or limit

    def _paginate(
            self,
            url: str,
            params: Dict,
            page_size: Optional[int],
            limit: Optional[int],
    ) -> PaginateResult:
        params = {k: v for k, v in (params or {}).items() if v is not None}
        page_size = self._get_pagination_page_size(page_size, limit)
        if page_size is None:
            response = self.session.get(url, params=params).json()
        else:
            response = self.session.get(url, params={'limit': page_size, **params}).json()
        result = PaginateResult(response.get('data', []), response.get('included', []))
        while 'next' in response['links'] and (limit is None or len(result.data) < limit):
            # Query params from previous pagination call can be included in the next URL
            # and duplicate parameters are not allowed, so we need to filter those out.
            parsed_url = parse.urlparse(response['links']['next'])
            included_params = parse.parse_qs(parsed_url.query)
            step_params = {k: v for k, v in params.items() if k not in included_params}
            response = self.session.get(response['links']['next'], params=step_params).json()
            result.data.extend(response['data'])
            result.included.extend(response.get('included', []))
        return result

    def paginate(self, url, params=None, page_size: Optional[int] = 100, limit=None) -> List[Dict]:
        return self._paginate(url, params, page_size, limit).data

    def paginate_with_included(self, url, params=None, page_size: Optional[int] = 100, limit=None) -> PaginateResult:
        return self._paginate(url, params, page_size, limit)

    @property
    def apps(self) -> Apps:
        return Apps(self)

    @property
    def app_store_versions(self) -> AppStoreVersions:
        return AppStoreVersions(self)

    @property
    def app_store_version_localizations(self) -> AppStoreVersionLocalizations:
        return AppStoreVersionLocalizations(self)

    @property
    def app_store_version_submissions(self) -> AppStoreVersionSubmissions:
        return AppStoreVersionSubmissions(self)

    @property
    def beta_app_review_submissions(self) -> BetaAppReviewSubmissions:
        return BetaAppReviewSubmissions(self)

    @property
    def beta_build_localizations(self) -> BetaBuildLocalizations:
        return BetaBuildLocalizations(self)

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
    def beta_groups(self) -> BetaGroups:
        return BetaGroups(self)

    @property
    def pre_release_versions(self) -> PreReleaseVersions:
        return PreReleaseVersions(self)

    @property
    def profiles(self) -> Profiles:
        return Profiles(self)

    @property
    def review_submissions(self) -> ReviewSubmissions:
        return ReviewSubmissions(self)

    @property
    def review_submissions_items(self) -> ReviewSubmissionItems:
        return ReviewSubmissionItems(self)

    @property
    def signing_certificates(self) -> SigningCertificates:
        return SigningCertificates(self)
