from __future__ import annotations

import time
from abc import ABCMeta
from typing import List
from typing import Optional
from typing import Union

from codemagic import cli
from codemagic.apple import AppStoreConnectApiError
from codemagic.apple.resources import App
from codemagic.apple.resources import BetaAppLocalization
from codemagic.apple.resources import Build
from codemagic.apple.resources import BuildProcessingState
from codemagic.apple.resources import Locale
from codemagic.apple.resources import PreReleaseVersion
from codemagic.apple.resources import ResourceId
from codemagic.cli import Colors

from ..abstract_base_action import AbstractBaseAction
from ..action_group import AppStoreConnectActionGroup
from ..arguments import BetaBuildInfo
from ..arguments import BuildArgument
from ..arguments import PublishArgument
from ..arguments import Types
from ..errors import AppStoreConnectError


class BuildsActionGroup(AbstractBaseAction, metaclass=ABCMeta):

    @cli.action('get',
                BuildArgument.BUILD_ID_RESOURCE_ID,
                action_group=AppStoreConnectActionGroup.BUILDS)
    def get_build(self, build_id: ResourceId, should_print: bool = True) -> Build:
        """
        Get information about a specific build
        """

        return self._get_resource(build_id, self.api_client.builds, should_print)

    @cli.action('pre-release-version',
                BuildArgument.BUILD_ID_RESOURCE_ID,
                action_group=AppStoreConnectActionGroup.BUILDS)
    def get_build_pre_release_version(self, build_id: ResourceId, should_print: bool = True) -> PreReleaseVersion:
        """
        Get the prerelease version for a specific build
        """

        return self._get_related_resource(
            build_id,
            Build,
            PreReleaseVersion,
            self.api_client.builds.read_pre_release_version,
            should_print,
        )

    @cli.action(
        'add-beta-test-info',
        BuildArgument.BUILD_ID_RESOURCE_ID,
        BuildArgument.BETA_BUILD_LOCALIZATIONS,
        BuildArgument.LOCALE_DEFAULT,
        BuildArgument.WHATS_NEW,
        action_group=AppStoreConnectActionGroup.BUILDS)
    def add_beta_test_info(
            self,
            build_id: ResourceId,
            beta_build_localizations: Optional[Union[List[BetaBuildInfo], Types.BetaBuildLocalizations]] = None,
            locale: Optional[Locale] = None,
            whats_new: Optional[Types.WhatsNewArgument] = None):
        """
        Add localized What's new (what to test) information
        """

        if isinstance(beta_build_localizations, Types.BetaBuildLocalizations):
            beta_test_info_items = beta_build_localizations.value
        else:
            beta_test_info_items = beta_build_localizations or []

        if whats_new:
            beta_test_info_items.append(BetaBuildInfo(whats_new=whats_new.value, locale=locale))

        self.logger.info(Colors.BLUE('\nUpdate beta build localization info in TestFlight for uploaded build'))
        for item in beta_test_info_items:
            self.create_beta_build_localization(build_id=build_id, locale=item.locale, whats_new=item.whats_new)

    @cli.action(
        'submit-to-testflight',
        BuildArgument.BUILD_ID_RESOURCE_ID,
        PublishArgument.MAX_BUILD_PROCESSING_WAIT,
        action_group=AppStoreConnectActionGroup.BUILDS)
    def submit_to_testflight(
            self,
            build_id: ResourceId,
            max_build_processing_wait: Optional[Union[int, Types.MaxBuildProcessingWait]] = None):
        """
        Submit build to TestFlight
        """

        # Workaround to support overriding default value by environment variable.
        if max_build_processing_wait is not None:
            if isinstance(max_build_processing_wait, Types.MaxBuildProcessingWait):
                max_processing_minutes = max_build_processing_wait.value
            else:
                max_processing_minutes = max_build_processing_wait
        else:
            max_processing_minutes = Types.MaxBuildProcessingWait.default_value

        self.logger.info(Colors.BLUE('\nSubmit uploaded build to TestFlight beta review'))

        build, app = self.api_client.builds.read_with_include(build_id, App)

        try:
            self._assert_app_has_testflight_information(app)
        except ValueError as ve:
            raise AppStoreConnectError(str(ve)) from ve

        if max_processing_minutes:
            build = self._wait_until_build_is_processed(build, max_processing_minutes)

        self.create_beta_app_review_submission(build.id)

    def _wait_until_build_is_processed(
        self,
        build: Build,
        max_processing_minutes: int,
        retry_wait_seconds: int = 30,
    ) -> Build:
        self.logger.info(
            Colors.BLUE(
                '\nProcessing of builds by Apple can take a while, the timeout for waiting the processing '
                'to finish for build %s is set to %d minutes.'),
            build.id,
            max_processing_minutes,
        )

        start_waiting = time.time()
        while time.time() - start_waiting < max_processing_minutes * 60:
            if build.attributes.processingState is BuildProcessingState.PROCESSING:
                msg_template = 'Build %s is still being processed on App Store Connect side, waiting %d seconds ' \
                               'and checking again'
                self.logger.info(msg_template, build.id, retry_wait_seconds)
                time.sleep(retry_wait_seconds)
                try:
                    build = self.api_client.builds.read(build)
                except AppStoreConnectApiError as api_error:
                    raise AppStoreConnectError(str(api_error))
            elif build.attributes.processingState in (BuildProcessingState.FAILED, BuildProcessingState.INVALID):
                raise IOError(f'Uploaded build {build.id} is {build.attributes.processingState.value.lower()}')
            else:
                self.logger.info(Colors.BLUE('Processing build %s is completed\n'), build.id)
                return build

        raise IOError((
            f'Waiting for build {build.id} processing timed out in {max_processing_minutes} minutes. '
            f'You can configure maximum timeout using {PublishArgument.MAX_BUILD_PROCESSING_WAIT.flag} '
            f'command line option, or {Types.MaxBuildProcessingWait.environment_variable_key} environment variable.'
        ))

    def _assert_app_has_testflight_information(self, app: App):
        missing_beta_app_information = self._get_missing_beta_app_information(app)
        missing_beta_app_review_information = self._get_missing_beta_app_review_information(app)

        if not missing_beta_app_information and not missing_beta_app_review_information:
            return  # All information required for TestFlight submission seems to be present

        error_lines = []
        if missing_beta_app_information:
            missing_values = ', '.join(missing_beta_app_information)
            error_lines.append(f'App is missing required Beta App Information: {missing_values}.')
        if missing_beta_app_review_information:
            missing_values = ', '.join(missing_beta_app_review_information)
            error_lines.append(f'App is missing required Beta App Review Information: {missing_values}.')

        name = app.attributes.name
        raise ValueError('\n'.join([
            f'Complete test information is required to submit application {name} build for external testing.',
            *error_lines,
            f'Fill in test information at https://appstoreconnect.apple.com/apps/{app.id}/testflight/test-info.',
        ]))

    def _get_missing_beta_app_information(self, app: App) -> List[str]:
        app_beta_localization = self._get_app_default_beta_localization(app)

        feedback_email = app_beta_localization.attributes.feedbackEmail if app_beta_localization else None
        required_test_information = {
            'Feedback Email': feedback_email,
        }
        return [field_name for field_name, value in required_test_information.items() if not value]

    def _get_missing_beta_app_review_information(self, app: App) -> List[str]:
        beta_app_review_detail = self.api_client.apps.read_beta_app_review_detail(app)
        required_test_information = {
            'First Name': beta_app_review_detail.attributes.contactFirstName,
            'Last Name': beta_app_review_detail.attributes.contactLastName,
            'Phone Number': beta_app_review_detail.attributes.contactPhone,
            'Email': beta_app_review_detail.attributes.contactEmail,
        }
        return [field_name for field_name, value in required_test_information.items() if not value]

    def _get_app_default_beta_localization(self, app: App) -> Optional[BetaAppLocalization]:
        beta_app_localizations = self.api_client.apps.list_beta_app_localizations(app)
        for beta_app_localization in beta_app_localizations:
            if beta_app_localization.attributes.locale.value == app.attributes.primaryLocale:
                return beta_app_localization
        # If nothing matches, then just take the first
        return beta_app_localizations[0] if beta_app_localizations else None
