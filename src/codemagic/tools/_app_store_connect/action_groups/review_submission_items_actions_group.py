from __future__ import annotations

from abc import ABCMeta
from typing import Optional

from codemagic import cli
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ReviewSubmissionItem

from ..abstract_base_action import AbstractBaseAction
from ..action_group import AppStoreConnectActionGroup
from ..arguments import AppStoreVersionArgument
from ..arguments import ReviewSubmissionArgument


class ReviewSubmissionItemsActionGroup(AbstractBaseAction, metaclass=ABCMeta):
    @cli.action(
        'create',
        AppStoreVersionArgument.APP_STORE_VERSION_ID,
        ReviewSubmissionArgument.APP_CUSTOM_PRODUCT_PAGE_VERSION_ID,
        ReviewSubmissionArgument.APP_EVENT_ID,
        ReviewSubmissionArgument.APP_STORE_VERSION_ID,
        ReviewSubmissionArgument.APP_STORE_VERSION_EXPERIMENT_ID,
        action_group=AppStoreConnectActionGroup.REVIEW_SUBMISSION_ITEMS,
    )
    def create_review_submission_item(
        self,
        review_submission_id: ResourceId,
        app_custom_product_page_version_id: Optional[ResourceId] = None,
        app_event_id: Optional[ResourceId] = None,
        app_store_version_id: Optional[ResourceId] = None,
        app_store_version_experiment_id: Optional[ResourceId] = None,
        should_print: bool = True,
    ) -> ReviewSubmissionItem:
        """
        Add contents to review submission for App Store review request
        """
        optional_kwargs = {
            'app_custom_product_page_version': app_custom_product_page_version_id,
            'app_event': app_event_id,
            'app_store_version': app_store_version_id,
            'app_store_version_experiment': app_store_version_experiment_id,
        }
        return self._create_resource(
            self.api_client.review_submissions_items,
            should_print,
            review_submission=review_submission_id,
            **{k: v for k, v in optional_kwargs.items() if v is not None},
        )
