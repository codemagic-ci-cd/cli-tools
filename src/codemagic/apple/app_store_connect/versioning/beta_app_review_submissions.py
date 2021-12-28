from dataclasses import dataclass
from typing import List
from typing import Optional
from typing import Type
from typing import Union

from codemagic.apple.app_store_connect.resource_manager import ResourceManager
from codemagic.apple.resources import BetaAppReviewSubmission
from codemagic.apple.resources import BetaReviewState
from codemagic.apple.resources import Build
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ResourceType


class BetaAppReviewSubmissions(ResourceManager[BetaAppReviewSubmission]):
    """
    Beta App Review Submissions
    https://developer.apple.com/documentation/appstoreconnectapi/prerelease_versions_and_beta_testers/beta_app_review_submissions
    """

    @property
    def resource_type(self) -> Type[BetaAppReviewSubmission]:
        return BetaAppReviewSubmission

    @dataclass
    class Filter(ResourceManager.Filter):
        beta_review_state: Optional[BetaReviewState] = None
        build: Optional[ResourceId] = None

    def create(self, build: Union[ResourceId, Build]) -> BetaAppReviewSubmission:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/submit_an_app_for_beta_review
        """
        relationships = {
            'build': {
                'data': self._get_attribute_data(build, ResourceType.BUILDS),
            },
        }
        payload = self._get_create_payload(
            ResourceType.BETA_APP_REVIEW_SUBMISSIONS, relationships=relationships)
        response = self.client.session.post(f'{self.client.API_URL}/betaAppReviewSubmissions', json=payload).json()
        return BetaAppReviewSubmission(response['data'], created=True)

    def list(self, resource_filter: Filter = Filter()) -> List[BetaAppReviewSubmission]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_beta_app_review_submissions
        """
        beta_review_submissions = self.client.paginate(
            f'{self.client.API_URL}/betaAppReviewSubmissions',
            params=resource_filter.as_query_params(),
        )
        return [BetaAppReviewSubmission(submission) for submission in beta_review_submissions]
