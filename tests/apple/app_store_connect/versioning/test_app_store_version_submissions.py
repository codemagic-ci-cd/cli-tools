import os

import pytest

from codemagic.apple.resources import AppStoreVersionSubmission
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ResourceType
from tests.apple.app_store_connect.resource_manager_test_base import ResourceManagerTestsBase


@pytest.mark.skipif(not os.environ.get('RUN_LIVE_API_TESTS'), reason='Live App Store Connect API access')
class AppStoreVersionSubmissionsTest(ResourceManagerTestsBase):
    def test_create(self):
        app_store_version_id = ResourceId('1525e3c9-3015-407a-9ba5-9addd2558224')
        app_store_version_submission = self.api_client.app_store_version_submissions.create(app_store_version_id)
        assert isinstance(app_store_version_submission, AppStoreVersionSubmission)
        assert app_store_version_submission.type is ResourceType.APP_STORE_VERSION_SUBMISSIONS
