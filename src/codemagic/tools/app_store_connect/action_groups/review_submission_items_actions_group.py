from __future__ import annotations

from abc import ABCMeta
from typing import TYPE_CHECKING
from typing import List
from typing import Optional
from typing import Union
from typing import cast

from codemagic import cli
from codemagic.apple.resources import AppStoreVersionLocalization
from codemagic.apple.resources import ErrorResponse
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ReviewSubmissionItem
from codemagic.cli import Colors
from codemagic.utilities import case_conversion

from ..abstract_base_action import AbstractBaseAction
from ..action_group import AppStoreConnectActionGroup
from ..arguments import CommonArgument
from ..arguments import ReviewSubmissionArgument
from ..arguments import ReviewSubmissionItemArgument
from ..errors import AppStoreConnectError

if TYPE_CHECKING:
    from codemagic.apple.app_store_connect.resource_manager import CreatingResourceManager


class ReviewSubmissionItemsActionGroup(AbstractBaseAction, metaclass=ABCMeta):
    @cli.action(
        "create",
        ReviewSubmissionArgument.REVIEW_SUBMISSION_ID,
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
            "app_custom_product_page_version": app_custom_product_page_version_id,
            "app_event": app_event_id,
            "app_store_version": app_store_version_id,
            "app_store_version_experiment": app_store_version_experiment_id,
        }
        try:
            return self._create_resource(
                cast("CreatingResourceManager[ReviewSubmissionItem]", self.api_client.review_submissions_items),
                should_print,
                review_submission=review_submission_id,
                **{k: v for k, v in optional_kwargs.items() if v is not None},
            )
        except AppStoreConnectError as asc_error:
            if asc_error.api_error:
                self._on_create_review_submission_item_error(asc_error.api_error)
            raise

    @cli.action(
        "delete",
        ReviewSubmissionItemArgument.REVIEW_SUBMISSION_ITEM_ID,
        CommonArgument.IGNORE_NOT_FOUND,
        action_group=AppStoreConnectActionGroup.REVIEW_SUBMISSION_ITEMS,
    )
    def delete_review_submission_item(
        self,
        review_submission_item_id: Union[ResourceId, ReviewSubmissionItem],
        ignore_not_found: bool = False,
    ) -> None:
        """
        Delete specified Review Submission item
        """
        self._delete_resource(
            self.api_client.review_submissions_items,
            review_submission_item_id,
            ignore_not_found,
        )

    def _on_create_review_submission_item_error(self, error_responses: ErrorResponse):
        """
        Show informative warning message if some required fields are missing
        for App Store Version localization whose locale matches with application's
        default locale.
        """

        missing_attributes = self._get_missing_required_attributes_names(error_responses)
        if not missing_attributes:
            return
        elif len(missing_attributes) == 1:
            attribute_names = missing_attributes[0]
        else:
            attribute_names = " and ".join([", ".join(missing_attributes[:-1]), missing_attributes[-1]])

        missing_default_locale_attributes_error = (
            f"\nCreating {ReviewSubmissionItem} failed. Please ensure that {AppStoreVersionLocalization} "
            f"for your application default locale defines {attribute_names}!\n"
        )
        self.echo(Colors.YELLOW(missing_default_locale_attributes_error))

    @classmethod
    def _get_missing_required_attributes_names(cls, error_responses: ErrorResponse) -> List[str]:
        """
        Extract names of fields that are undefined for application's
        default locale App Store Version localization
        """
        default_locale_missing_values = set()

        for associated_error in error_responses.iter_associated_errors():
            if associated_error.code == "ENTITY_ERROR.ATTRIBUTE.REQUIRED" and associated_error.source_pointer:
                # source pointer is like '/data/attributes/keywords'
                asc_field_name = associated_error.source_pointer.split("/")[-1]
                field_name = case_conversion.camel_to_snake(asc_field_name).replace("_", " ").lower()
                default_locale_missing_values.add(field_name.replace(" url", " URL"))

        return list(default_locale_missing_values)
