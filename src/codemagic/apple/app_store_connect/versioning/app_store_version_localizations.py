from typing import Optional
from typing import Type
from typing import Union

from codemagic.apple.app_store_connect.resource_manager import ResourceManager
from codemagic.apple.resources import AppStoreVersion
from codemagic.apple.resources import AppStoreVersionLocalization
from codemagic.apple.resources import LinkedResourceData
from codemagic.apple.resources import Locale
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ResourceType


class AppStoreVersionLocalizations(ResourceManager[AppStoreVersionLocalization]):
    """
    App Store Version Localizations
    https://developer.apple.com/documentation/appstoreconnectapi/app_metadata/app_store_version_localizations
    """

    @property
    def resource_type(self) -> Type[AppStoreVersionLocalization]:
        return AppStoreVersionLocalization

    def read(
        self,
        app_store_version_localization: Union[LinkedResourceData, ResourceId],
    ) -> AppStoreVersionLocalization:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/read_app_store_version_localization_information
        """
        app_store_version_localization_id = self._get_resource_id(app_store_version_localization)
        response = self.client.session.get(
            f'{self.client.API_URL}/appStoreVersionLocalizations/{app_store_version_localization_id}',
        ).json()
        return AppStoreVersionLocalization(response['data'])

    def create(
        self,
        app_store_version: Union[ResourceId, AppStoreVersion],
        locale: Locale,
        description: Optional[str] = None,
        keywords: Optional[str] = None,
        marketing_url: Optional[str] = None,
        promotional_text: Optional[str] = None,
        support_url: Optional[str] = None,
        whats_new: Optional[str] = None,
    ) -> AppStoreVersionLocalization:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/create_an_app_store_version_localization
        """
        attributes = {
            'locale': locale.value,
            **self._construct_payload_attributes(
                description=description,
                keywords=keywords,
                marketing_url=marketing_url,
                promotional_text=promotional_text,
                support_url=support_url,
                whats_new=whats_new,
            ),
        }

        relationships = {
            'appStoreVersion': {
                'data': self._get_attribute_data(app_store_version, ResourceType.APP_STORE_VERSIONS),
            },
        }

        payload = self._get_create_payload(
            ResourceType.APP_STORE_VERSION_LOCALIZATIONS,
            attributes=attributes,
            relationships=relationships,
        )
        response = self.client.session.post(f'{self.client.API_URL}/appStoreVersionLocalizations', json=payload).json()
        return AppStoreVersionLocalization(response['data'], created=True)

    def modify(
        self,
        app_store_version_localization: Union[ResourceId, AppStoreVersionLocalization],
        description: Optional[str] = None,
        keywords: Optional[str] = None,
        marketing_url: Optional[str] = None,
        promotional_text: Optional[str] = None,
        support_url: Optional[str] = None,
        whats_new: Optional[str] = None,
    ) -> AppStoreVersionLocalization:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/modify_an_app_store_version_localization
        """
        attributes = self._construct_payload_attributes(
            description=description,
            keywords=keywords,
            marketing_url=marketing_url,
            promotional_text=promotional_text,
            support_url=support_url,
            whats_new=whats_new,
        )
        app_store_version_localization_id = self._get_resource_id(app_store_version_localization)
        payload = self._get_update_payload(
            app_store_version_localization_id,
            ResourceType.APP_STORE_VERSION_LOCALIZATIONS,
            attributes=attributes,
        )
        response = self.client.session.patch(
            f'{self.client.API_URL}/appStoreVersionLocalizations/{app_store_version_localization_id}',
            json=payload,
        ).json()
        return AppStoreVersionLocalization(response['data'])

    def delete(
        self,
        app_store_version_localization: Union[ResourceId, AppStoreVersionLocalization],
    ) -> None:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/delete_an_app_store_version_localization
        """
        app_store_version_localization_id = self._get_resource_id(app_store_version_localization)
        self.client.session.delete(
            f'{self.client.API_URL}/appStoreVersionLocalizations/{app_store_version_localization_id}',
        )

    @classmethod
    def _construct_payload_attributes(
        cls,
        description: Optional[str] = None,
        keywords: Optional[str] = None,
        marketing_url: Optional[str] = None,
        promotional_text: Optional[str] = None,
        support_url: Optional[str] = None,
        whats_new: Optional[str] = None,
    ):
        attributes = {}
        if description is not None:
            attributes['description'] = description
        if keywords is not None:
            attributes['keywords'] = keywords
        if marketing_url is not None:
            attributes['marketingUrl'] = marketing_url
        if promotional_text is not None:
            attributes['promotionalText'] = promotional_text
        if support_url is not None:
            attributes['supportUrl'] = support_url
        if whats_new is not None:
            attributes['whatsNew'] = whats_new
        return attributes
