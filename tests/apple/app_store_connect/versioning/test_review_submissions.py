import os

import pytest

from codemagic.apple.resources import Platform
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ResourceType
from codemagic.apple.resources import ReviewSubmission
from tests.apple.app_store_connect.resource_manager_test_base import ResourceManagerTestsBase


@pytest.mark.skipif(not os.environ.get('RUN_LIVE_API_TESTS'), reason='Live App Store Connect API access')
class ReviewSubmissionsTest(ResourceManagerTestsBase):
    def test_create(self):
        app_id = ResourceId('1481211155')  # Banaan
        review_submission = self.api_client.review_submissions.create(
            Platform.IOS,
            app_id,
        )
        assert isinstance(review_submission, ReviewSubmission)
        assert review_submission.type is ResourceType.REVIEW_SUBMISSIONS

    def test_read(self):
        review_submission_id = ResourceId('6e2682ef-873d-4ced-985a-787b6bd6bd7c')
        review_submission = self.api_client.review_submissions.read(review_submission_id)
        print(review_submission.json())
        assert isinstance(review_submission, ReviewSubmission)
        assert review_submission.type is ResourceType.REVIEW_SUBMISSIONS
        assert review_submission.id == review_submission_id
