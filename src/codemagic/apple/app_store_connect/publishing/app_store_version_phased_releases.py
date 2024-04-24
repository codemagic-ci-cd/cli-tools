from typing import Type

from codemagic.apple.app_store_connect.resource_manager import ResourceManager
from codemagic.apple.resources import AppStoreVersionPhasedRelease


class AppStoreVersionPhasedReleases(ResourceManager[AppStoreVersionPhasedRelease]):
    """
    App Store Version Phased Releases
    https://developer.apple.com/documentation/appstoreconnectapi/app_store/app_store_version_phased_releases

    """

    @property
    def resource_type(self) -> Type[AppStoreVersionPhasedRelease]:
        return AppStoreVersionPhasedRelease

    def create(self, *args, **kwargs) -> AppStoreVersionPhasedRelease:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/create_an_app_store_version_phased_release
        """
        raise NotImplementedError()

    def modify(self, *args, **kwargs) -> AppStoreVersionPhasedRelease:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/modify_an_app_store_version_phased_release
        """
        raise NotImplementedError()

    def delete(self, *args, **kwargs) -> None:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/delete_an_app_store_version_phased_release
        """
        raise NotImplementedError()
