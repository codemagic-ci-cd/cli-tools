from __future__ import annotations

from abc import ABCMeta
from typing import List
from typing import Optional

from codemagic import cli
from codemagic.apple.resources import AppStoreVersionSubmission
from codemagic.apple.resources import BetaAppReviewSubmission
from codemagic.apple.resources import BetaReviewState
from codemagic.apple.resources import ResourceId

from ..abstract_base_action import AbstractBaseAction
from ..action_group import AppStoreConnectActionGroup
from ..arguments import BuildArgument


class BetaAppReviewSubmissionsActionGroup(AbstractBaseAction, metaclass=ABCMeta):

    @cli.action('create',
                BuildArgument.BUILD_ID_RESOURCE_ID,
                action_group=AppStoreConnectActionGroup.BETA_APP_REVIEW_SUBMISSIONS)
    def create_beta_app_review_submission(
            self, build_id: ResourceId, should_print: bool = True) -> AppStoreVersionSubmission:
        """
        Submit an app for beta app review to allow external testing
        """

        return self._create_resource(
            self.api_client.beta_app_review_submissions,
            should_print,
            build=build_id,
        )

    @cli.action('list',
                BuildArgument.BUILD_ID_RESOURCE_ID,
                action_group=AppStoreConnectActionGroup.BETA_APP_REVIEW_SUBMISSIONS)
    def list_beta_app_review_submissions(
            self,
            build_id: Optional[ResourceId],
            beta_review_state: Optional[BetaReviewState] = None,
            should_print: bool = True) -> List[BetaAppReviewSubmission]:
        """
        Find and list beta app review submissions of a build
        """

        beta_app_review_submissions_filter = self.api_client.beta_app_review_submissions.Filter(
            build=build_id,
            beta_review_state=beta_review_state)
        return self._list_resources(
            beta_app_review_submissions_filter,
            self.api_client.beta_app_review_submissions,
            should_print,
        )
