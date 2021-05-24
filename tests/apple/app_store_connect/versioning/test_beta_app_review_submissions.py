import os

import pytest

from codemagic.apple.resources import BetaAppReviewSubmission
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ResourceType
from tests.apple.app_store_connect.resource_manager_test_base import ResourceManagerTestsBase


@pytest.mark.skipif(not os.environ.get('RUN_LIVE_API_TESTS'), reason='Live App Store Connect API access')
class BetaAppReviewSubmissionsTest(ResourceManagerTestsBase):
    def test_list(self):
        resource_filter = self.api_client.beta_app_review_submissions.Filter(
            build=ResourceId('1525e3c9-3015-407a-9ba5-9addd2558224'),
        )
        beta_app_review_submissions = self.api_client.beta_app_review_submissions.list(resource_filter)
        assert len(beta_app_review_submissions) > 0
        for beta_app_review_submission in beta_app_review_submissions:
            assert isinstance(beta_app_review_submission, BetaAppReviewSubmission)
            assert beta_app_review_submission.type is ResourceType.BETA_APP_REVIEW_SUBMISSIONS

    def test_create(self):
        beta_app_review_submission = self.api_client.beta_app_review_submissions.create(
            build=ResourceId('1525e3c9-3015-407a-9ba5-9addd2558224'),
        )
        assert isinstance(beta_app_review_submission, BetaAppReviewSubmission)
        assert beta_app_review_submission.type is ResourceType.BETA_APP_REVIEW_SUBMISSIONS
