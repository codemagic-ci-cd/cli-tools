from dataclasses import dataclass
from typing import List
from typing import Optional
from typing import Type
from typing import Union

from codemagic.apple.app_store_connect.resource_manager import ResourceManager
from codemagic.apple.resources import Build
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ResourceType
from codemagic.apple.resources.beta_build_localization import BetaBuildLocalization
from codemagic.apple.resources.enums import Locale


class BetaBuildLocalizations(ResourceManager[BetaBuildLocalization]):
    """
    Beta Build Localizations
    https://developer.apple.com/documentation/appstoreconnectapi/prerelease_versions_and_beta_testers/beta_build_localizations
    """

    @property
    def resource_type(self) -> Type[BetaBuildLocalization]:
        return BetaBuildLocalization

    @dataclass
    class Filter(ResourceManager.Filter):
        build: Optional[ResourceId] = None
        locale: Optional[Locale] = None

    def create(self, build: Union[ResourceId, Build], locale: Locale, whats_new: str) -> BetaBuildLocalization:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/create_a_beta_build_localization
        """
        attributes = {
            'locale': str(locale),
            'whatsNew': whats_new,
        }

        relationships = {
            'build': {
                'data': self._get_attribute_data(build, ResourceType.BUILDS),
            },
        }

        payload = self._get_create_payload(
            ResourceType.BETA_BUILD_LOCALIZATIONS, attributes=attributes, relationships=relationships)
        response = self.client.session.post(f'{self.client.API_URL}/betaBuildLocalizations', json=payload).json()
        return BetaBuildLocalization(response['data'], created=True)

    def modify(self, resource_id: ResourceId, whats_new: str) -> BetaBuildLocalization:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/modify_a_beta_build_localization
        """
        payload = self._get_update_payload(
            resource_id, ResourceType.BETA_BUILD_LOCALIZATIONS, attributes={'whatsNew': whats_new})

        response = self.client.session.patch(
            f'{self.client.API_URL}/betaBuildLocalizations/{resource_id}', json=payload).json()
        return BetaBuildLocalization(response['data'])

    def list(self, resource_filter: Filter = Filter()) -> List[BetaBuildLocalization]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_beta_app_localizations
        """
        beta_build_localizations = self.client.paginate(
            f'{self.client.API_URL}/betaBuildLocalizations', params=resource_filter.as_query_params())
        return [BetaBuildLocalization(localization) for localization in beta_build_localizations]

    def delete(self, resource_id: ResourceId):
        """
        https://developer.apple.com/documentation/appstoreconnectapi/delete_a_beta_build_localization
        """
        self.client.session.delete(f'{self.client.API_URL}/betaBuildLocalizations/{resource_id}')
