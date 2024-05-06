from __future__ import annotations

from abc import ABCMeta
from typing import TYPE_CHECKING
from typing import List
from typing import cast

from codemagic import cli
from codemagic.apple.resources import Platform
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ReviewSubmission
from codemagic.apple.resources import ReviewSubmissionItem

from ..abstract_base_action import AbstractBaseAction
from ..action_group import AppStoreConnectActionGroup
from ..arguments import AppArgument
from ..arguments import AppStoreVersionArgument
from ..arguments import ReviewSubmissionArgument

if TYPE_CHECKING:
    from codemagic.apple.app_store_connect.resource_manager import CreatingResourceManager
    from codemagic.apple.app_store_connect.resource_manager import ModifyingResourceManager


class ReviewSubmissionsActionGroup(AbstractBaseAction, metaclass=ABCMeta):
    @cli.action(
        "create",
        AppArgument.APPLICATION_ID_RESOURCE_ID,
        AppStoreVersionArgument.PLATFORM,
        action_group=AppStoreConnectActionGroup.REVIEW_SUBMISSIONS,
    )
    def create_review_submission(
        self,
        application_id: ResourceId,
        platform: Platform,
        should_print: bool = True,
    ) -> ReviewSubmission:
        """
        Create a review submission request for application's latest App Store Version
        """
        return self._create_resource(
            cast("CreatingResourceManager[ReviewSubmission]", self.api_client.review_submissions),
            should_print,
            app=application_id,
            platform=platform,
        )

    @cli.action(
        "get",
        ReviewSubmissionArgument.REVIEW_SUBMISSION_ID,
        action_group=AppStoreConnectActionGroup.REVIEW_SUBMISSIONS,
    )
    def get_review_submission(
        self,
        review_submission_id: ResourceId,
        should_print: bool = True,
    ) -> ReviewSubmission:
        """
        Read Review Submission information
        """
        return self._get_resource(
            review_submission_id,
            self.api_client.review_submissions,
            should_print,
        )

    @cli.action(
        "cancel",
        ReviewSubmissionArgument.REVIEW_SUBMISSION_ID,
        action_group=AppStoreConnectActionGroup.REVIEW_SUBMISSIONS,
    )
    def cancel_review_submission(
        self,
        review_submission_id: ResourceId,
        should_print: bool = True,
    ) -> ReviewSubmission:
        """
        Discard a specific review submission from App Review
        """
        return self._modify_resource(
            cast("ModifyingResourceManager[ReviewSubmission]", self.api_client.review_submissions),
            review_submission_id,
            should_print,
            canceled=True,
        )

    @cli.action(
        "confirm",
        ReviewSubmissionArgument.REVIEW_SUBMISSION_ID,
        action_group=AppStoreConnectActionGroup.REVIEW_SUBMISSIONS,
    )
    def confirm_review_submission(
        self,
        review_submission_id: ResourceId,
        should_print: bool = True,
    ) -> ReviewSubmission:
        """
        Confirm pending review submission for App Review
        """
        return self._modify_resource(
            cast("ModifyingResourceManager[ReviewSubmission]", self.api_client.review_submissions),
            review_submission_id,
            should_print,
            submitted=True,
        )

    @cli.action(
        "items",
        ReviewSubmissionArgument.REVIEW_SUBMISSION_ID,
        action_group=AppStoreConnectActionGroup.REVIEW_SUBMISSIONS,
    )
    def list_review_submission_items(self, review_submission_id: ResourceId) -> List[ReviewSubmissionItem]:
        """
        List review submission items for specified review submission
        """
        return self._list_related_resources(
            resource_reference=review_submission_id,
            resource_type=ReviewSubmission,
            related_resource_type=ReviewSubmissionItem,
            list_related_resources_method=self.api_client.review_submissions.list_items,
            resource_filter=None,
            should_print=True,
        )
