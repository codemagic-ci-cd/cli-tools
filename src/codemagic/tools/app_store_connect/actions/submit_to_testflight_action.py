from __future__ import annotations

from abc import ABCMeta
from typing import List
from typing import Optional
from typing import Union

from codemagic import cli
from codemagic.apple import AppStoreConnectApiError
from codemagic.apple.resources import App
from codemagic.apple.resources import BetaAppLocalization
from codemagic.apple.resources import BetaAppReviewSubmission
from codemagic.apple.resources import ResourceId
from codemagic.cli import Colors

from ..abstract_base_action import AbstractBaseAction
from ..action_group import AppStoreConnectActionGroup
from ..arguments import ArgumentGroups
from ..arguments import BuildArgument
from ..arguments import Types
from ..errors import AppStoreConnectError


class SubmitToTestFlightAction(AbstractBaseAction, metaclass=ABCMeta):
    @cli.action(
        "submit-to-testflight",
        BuildArgument.BUILD_ID_RESOURCE_ID,
        *ArgumentGroups.SUBMIT_TO_TESTFLIGHT_OPTIONAL_ARGUMENTS,
        action_group=AppStoreConnectActionGroup.BUILDS,
    )
    def submit_to_testflight(
        self,
        build_id: ResourceId,
        max_build_processing_wait: Optional[Union[int, Types.MaxBuildProcessingWait]] = None,
        expire_build_submitted_for_review: bool = False,
    ) -> BetaAppReviewSubmission:
        """
        Submit build to TestFlight
        """

        max_processing_minutes = Types.MaxBuildProcessingWait.resolve_value(max_build_processing_wait)

        self.logger.info(Colors.BLUE(f"\nSubmit build {build_id!r} to TestFlight beta review"))

        try:
            build, app = self.api_client.builds.read_with_include(build_id, App)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error)) from api_error

        try:
            self._assert_app_has_testflight_information(app)
        except ValueError as ve:
            raise AppStoreConnectError(str(ve)) from ve

        if max_processing_minutes:
            build = self.wait_until_build_is_processed(build, max_processing_minutes)

        if expire_build_submitted_for_review:
            pre_release_version = self.api_client.builds.read_pre_release_version(build)
            self.logger.info(Colors.BLUE("\nExpire previous build before creating submission"))
            self.expire_build_submitted_for_review(
                application_id=app.id,
                platform=pre_release_version.attributes.platform if pre_release_version else None,
                should_print=False,
            )

        return self.create_beta_app_review_submission(build.id)

    def _assert_app_has_testflight_information(self, app: App):
        missing_beta_app_information = self._get_missing_beta_app_information(app)
        missing_beta_app_review_information = self._get_missing_beta_app_review_information(app)

        if not missing_beta_app_information and not missing_beta_app_review_information:
            return  # All information required for TestFlight submission seems to be present

        error_lines = []
        if missing_beta_app_information:
            missing_values = ", ".join(missing_beta_app_information)
            error_lines.append(f"App is missing required Beta App Information: {missing_values}.")
        if missing_beta_app_review_information:
            missing_values = ", ".join(missing_beta_app_review_information)
            error_lines.append(f"App is missing required Beta App Review Information: {missing_values}.")

        name = app.attributes.name
        raise ValueError(
            "\n".join(
                [
                    f"Complete test information is required to submit application {name} build for external testing.",
                    *error_lines,
                    f"Fill in test information at https://appstoreconnect.apple.com/apps/{app.id}/testflight/test-info.",
                ],
            ),
        )

    def _get_missing_beta_app_information(self, app: App) -> List[str]:
        app_beta_localization = self._get_app_default_beta_localization(app)

        feedback_email = app_beta_localization.attributes.feedbackEmail if app_beta_localization else None
        required_test_information = {
            "Feedback Email": feedback_email,
        }
        return [field_name for field_name, value in required_test_information.items() if not value]

    def _get_missing_beta_app_review_information(self, app: App) -> List[str]:
        beta_app_review_detail = self.api_client.apps.read_beta_app_review_detail(app)
        required_test_information = {
            "First Name": beta_app_review_detail.attributes.contactFirstName,
            "Last Name": beta_app_review_detail.attributes.contactLastName,
            "Phone Number": beta_app_review_detail.attributes.contactPhone,
            "Email": beta_app_review_detail.attributes.contactEmail,
        }
        return [field_name for field_name, value in required_test_information.items() if not value]

    def _get_app_default_beta_localization(self, app: App) -> Optional[BetaAppLocalization]:
        beta_app_localizations = self.api_client.apps.list_beta_app_localizations(app)
        for beta_app_localization in beta_app_localizations:
            if beta_app_localization.attributes.locale is app.attributes.primaryLocale:
                return beta_app_localization
        # If nothing matches, then just take the first
        return beta_app_localizations[0] if beta_app_localizations else None
