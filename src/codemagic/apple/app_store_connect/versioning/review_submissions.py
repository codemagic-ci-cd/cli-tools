from typing import Optional
from typing import Type
from typing import Union

from codemagic.apple.app_store_connect.resource_manager import ResourceManager
from codemagic.apple.resources import App
from codemagic.apple.resources import LinkedResourceData
from codemagic.apple.resources import Platform
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ResourceType
from codemagic.apple.resources import ReviewSubmission


class ReviewSubmissions(ResourceManager[ReviewSubmission]):
    """
    Review Submissions
    https://developer.apple.com/documentation/appstoreconnectapi/review_submissions
    """

    @property
    def resource_type(self) -> Type[ReviewSubmission]:
        return ReviewSubmission

    def create(
        self,
        platform: Platform,
        app: Union[ResourceId, App],
    ) -> ReviewSubmission:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/post_v1_reviewsubmissions
        """
        attributes = {
            'platform': platform.value,
        }

        relationships = {
            'app': {
                'data': self._get_attribute_data(app, ResourceType.APPS),
            },
        }

        payload = self._get_create_payload(
            ResourceType.REVIEW_SUBMISSIONS,
            attributes=attributes,
            relationships=relationships,
        )
        response = self.client.session.post(f'{self.client.API_URL}/reviewSubmissions', json=payload).json()
        return ReviewSubmission(response['data'], created=True)

    def read(self, review_submission: Union[LinkedResourceData, ResourceId]) -> ReviewSubmission:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/get_v1_reviewsubmissions_id
        """
        review_submission_id = self._get_resource_id(review_submission)
        response = self.client.session.get(f'{self.client.API_URL}/reviewSubmissions/{review_submission_id}').json()
        return ReviewSubmission(response['data'])

    def modify(
        self,
        review_submission: Union[LinkedResourceData, ResourceId],
        canceled: Optional[bool] = None,
        submitted: Optional[bool] = None,
    ) -> ReviewSubmission:
        review_submission_id = self._get_resource_id(review_submission)

        attributes = {}
        if canceled is not None:
            attributes['canceled'] = canceled
        if submitted is not None:
            attributes['submitted'] = submitted

        payload = self._get_update_payload(
            review_submission_id,
            ResourceType.REVIEW_SUBMISSIONS,
            attributes=attributes,
        )
        response = self.client.session.patch(
            f'{self.client.API_URL}/reviewSubmissions/{review_submission_id}',
            json=payload,
        ).json()
        return ReviewSubmission(response['data'])
