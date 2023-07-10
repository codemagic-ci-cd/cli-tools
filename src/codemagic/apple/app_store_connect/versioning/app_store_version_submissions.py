from typing import Type
from typing import Union

from codemagic.apple.app_store_connect.resource_manager import ResourceManager
from codemagic.apple.resources import AppStoreVersion
from codemagic.apple.resources import AppStoreVersionSubmission
from codemagic.apple.resources import LinkedResourceData
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ResourceType


class AppStoreVersionSubmissions(ResourceManager[AppStoreVersionSubmission]):
    """
    App Store Version Submissions
    https://developer.apple.com/documentation/appstoreconnectapi/app_store_version_submissions
    """

    @property
    def resource_type(self) -> Type[AppStoreVersionSubmission]:
        return AppStoreVersionSubmission

    def create(self, app_store_version: Union[ResourceId, AppStoreVersion]) -> AppStoreVersionSubmission:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/create_an_app_store_version_submission
        """
        relationships = {
            "appStoreVersion": {
                "data": self._get_attribute_data(app_store_version, ResourceType.APP_STORE_VERSIONS),
            },
        }
        payload = self._get_create_payload(ResourceType.APP_STORE_VERSION_SUBMISSIONS, relationships=relationships)
        response = self.client.session.post(f"{self.client.API_URL}/appStoreVersionSubmissions", json=payload).json()
        return AppStoreVersionSubmission(response["data"], created=True)

    def delete(self, app_store_version_submission: Union[LinkedResourceData, ResourceId]):
        """
        https://developer.apple.com/documentation/appstoreconnectapi/delete_an_app_store_version_submission
        """
        submission_id = self._get_resource_id(app_store_version_submission)
        self.client.session.delete(f"{self.client.API_URL}/appStoreVersionSubmissions/{submission_id}")
