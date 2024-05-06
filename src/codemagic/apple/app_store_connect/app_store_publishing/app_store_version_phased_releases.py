from typing import Optional
from typing import Type
from typing import Union

from codemagic.apple.app_store_connect.resource_manager import ResourceManager
from codemagic.apple.resources import AppStoreVersionPhasedRelease
from codemagic.apple.resources import LinkedResourceData
from codemagic.apple.resources import PhasedReleaseState
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ResourceType


class AppStoreVersionPhasedReleases(ResourceManager[AppStoreVersionPhasedRelease]):
    """
    App Store Version Phased Releases
    https://developer.apple.com/documentation/appstoreconnectapi/app_store/app_store_version_phased_releases
    """

    @property
    def resource_type(self) -> Type[AppStoreVersionPhasedRelease]:
        return AppStoreVersionPhasedRelease

    def create(
        self,
        app_store_version: Union[ResourceId, LinkedResourceData],
        phased_release_state: Optional[PhasedReleaseState] = None,
    ) -> AppStoreVersionPhasedRelease:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/create_an_app_store_version_phased_release
        """
        if phased_release_state:
            attributes = {
                "phasedReleaseState": phased_release_state.value,
            }
        else:
            attributes = None

        relationships = {
            "appStoreVersion": {
                "data": self._get_attribute_data(app_store_version, ResourceType.APP_STORE_VERSIONS),
            },
        }

        payload = self._get_create_payload(
            ResourceType.APP_STORE_VERSION_PHASED_RELEASES,
            attributes=attributes,
            relationships=relationships,
        )

        response = self.client.session.post(
            f"{self.client.API_URL}/appStoreVersionPhasedReleases",
            json=payload,
        ).json()
        return AppStoreVersionPhasedRelease(response["data"], created=True)

    def modify(
        self,
        app_store_version_phased_release: Union[LinkedResourceData, ResourceId],
        *,
        phased_release_state: PhasedReleaseState,
    ) -> AppStoreVersionPhasedRelease:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/modify_an_app_store_version_phased_release
        """
        app_store_version_phased_release_id = self._get_resource_id(app_store_version_phased_release)

        attributes = {
            "phasedReleaseState": phased_release_state.value,
        }

        payload = self._get_update_payload(
            app_store_version_phased_release_id,
            ResourceType.APP_STORE_VERSION_PHASED_RELEASES,
            attributes=attributes,
        )

        response = self.client.session.patch(
            f"{self.client.API_URL}/appStoreVersionPhasedReleases/{app_store_version_phased_release_id}",
            json=payload,
        ).json()
        return AppStoreVersionPhasedRelease(response["data"])

    def delete(self, app_store_version_phased_release: Union[LinkedResourceData, ResourceId]) -> None:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/delete_an_app_store_version_phased_release
        """
        app_store_version_phased_release_id = self._get_resource_id(app_store_version_phased_release)

        self.client.session.delete(
            f"{self.client.API_URL}/appStoreVersionPhasedReleases/{app_store_version_phased_release_id}",
        )
