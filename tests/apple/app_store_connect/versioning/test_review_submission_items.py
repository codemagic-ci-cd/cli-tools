import os

import pytest

from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ResourceType
from codemagic.apple.resources import ReviewSubmissionItem
from tests.apple.app_store_connect.resource_manager_test_base import ResourceManagerTestsBase


@pytest.mark.skipif(not os.environ.get('RUN_LIVE_API_TESTS'), reason='Live App Store Connect API access')
class ReviewSubmissionItemsTest(ResourceManagerTestsBase):
    def test_create(self):
        review_submission_id = ResourceId('6e2682ef-873d-4ced-985a-787b6bd6bd7c')
        app_store_version_id = ResourceId('409ebefb-ebd1-4f1a-903d-6ba16e013ebf')
        review_submission_item = self.api_client.review_submissions_items.create(
            review_submission_id,
            app_store_version=app_store_version_id,
        )
        assert isinstance(review_submission_item, ReviewSubmissionItem)
        assert review_submission_item.type is ResourceType.REVIEW_SUBMISSION_ITEMS

    def test_delete(self):
        review_submission_item_id = ResourceId('NmUyNjgyZWYtODczZC00Y2VkLTk4NWEtNzg3YjZiZDZiZDdjfDZ8ODMyOTAzMTI0')
        self.api_client.review_submissions_items.delete(review_submission_item_id)
