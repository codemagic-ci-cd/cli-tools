from typing import Optional
from typing import Type
from typing import Union

from codemagic.apple.app_store_connect.resource_manager import ResourceManager
from codemagic.apple.resources import AppStoreVersion
from codemagic.apple.resources import LinkedResourceData
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ResourceType
from codemagic.apple.resources import ReviewSubmission
from codemagic.apple.resources import ReviewSubmissionItem


class ReviewSubmissionItems(ResourceManager[ReviewSubmissionItem]):
    """
    Review Submission Items
    https://developer.apple.com/documentation/appstoreconnectapi/review_submission_items
    """

    @property
    def resource_type(self) -> Type[ReviewSubmissionItem]:
        return ReviewSubmissionItem

    def create(
        self,
        review_submission: Union[ResourceId, ReviewSubmission],
        app_store_version: Optional[Union[ResourceId, AppStoreVersion]] = None,
    ) -> ReviewSubmissionItem:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/post_v1_reviewsubmissionitems
        """
        relationships = {
            'reviewSubmission': {
                'data': self._get_attribute_data(review_submission, ResourceType.REVIEW_SUBMISSIONS),
            },
        }
        if app_store_version is not None:
            relationships['appStoreVersion'] = {
                'data': self._get_attribute_data(app_store_version, ResourceType.APP_STORE_VERSIONS),
            }

        payload = self._get_create_payload(
            ResourceType.REVIEW_SUBMISSION_ITEMS,
            relationships=relationships,
        )
        response = self.client.session.post(f'{self.client.API_URL}/reviewSubmissionItems', json=payload).json()
        return ReviewSubmissionItem(response['data'], created=True)

    def delete(self, review_submission_item: Union[LinkedResourceData, ResourceId]):
        """
        https://developer.apple.com/documentation/appstoreconnectapi/delete_v1_reviewsubmissionitems_id
        """
        review_submission_item_id = self._get_resource_id(review_submission_item)
        self.client.session.delete(f'{self.client.API_URL}/reviewSubmissionItems/{review_submission_item_id}')
