from __future__ import annotations

from abc import ABCMeta

from codemagic import cli
from codemagic.apple.resources import AppStoreVersionSubmission
from codemagic.apple.resources import ResourceId

from ..abstract_base_action import AbstractBaseAction
from ..action_group import AppStoreConnectActionGroup
from ..arguments import AppStoreVersionArgument
from ..arguments import CommonArgument


class AppStoreVersionSubmissionsActionGroup(AbstractBaseAction, metaclass=ABCMeta):

    @cli.action('create',
                AppStoreVersionArgument.APP_STORE_VERSION_ID,
                action_group=AppStoreConnectActionGroup.APP_STORE_VERSION_SUBMISSIONS)
    def create_app_store_version_submission(self,
                                            app_store_version_id: ResourceId,
                                            should_print: bool = True) -> AppStoreVersionSubmission:
        """
        Submit an App Store Version to App Review
        """
        return self._create_resource(
            self.api_client.app_store_version_submissions,
            should_print,
            app_store_version=app_store_version_id,
        )

    @cli.action('delete',
                AppStoreVersionArgument.APP_STORE_VERSION_SUBMISSION_ID,
                CommonArgument.IGNORE_NOT_FOUND,
                action_group=AppStoreConnectActionGroup.APP_STORE_VERSION_SUBMISSIONS)
    def delete_app_store_version_submission(self,
                                            app_store_version_submission_id: ResourceId,
                                            ignore_not_found: bool = False) -> None:
        """
        Remove a version submission from App Store review
        """
        self._delete_resource(
            self.api_client.app_store_version_submissions,
            app_store_version_submission_id,
            ignore_not_found=ignore_not_found,
        )
