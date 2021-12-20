from __future__ import annotations

import shlex
import time
from abc import ABCMeta
from datetime import datetime
from distutils.version import LooseVersion
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from codemagic import cli
from codemagic.apple import AppStoreConnectApiError
from codemagic.apple.resources import App
from codemagic.apple.resources import AppStoreState
from codemagic.apple.resources import AppStoreVersion
from codemagic.apple.resources import AppStoreVersionLocalization
from codemagic.apple.resources import AppStoreVersionSubmission
from codemagic.apple.resources import BetaAppLocalization
from codemagic.apple.resources import BetaAppReviewSubmission
from codemagic.apple.resources import Build
from codemagic.apple.resources import BuildProcessingState
from codemagic.apple.resources import Locale
from codemagic.apple.resources import Platform
from codemagic.apple.resources import PreReleaseVersion
from codemagic.apple.resources import ReleaseType
from codemagic.apple.resources import ResourceId
from codemagic.cli import Colors

from ..abstract_base_action import AbstractBaseAction
from ..action_group import AppStoreConnectActionGroup
from ..arguments import AppStoreVersionArgument
from ..arguments import AppStoreVersionInfo
from ..arguments import AppStoreVersionLocalizationInfo
from ..arguments import ArgumentGroups
from ..arguments import BetaBuildInfo
from ..arguments import BuildArgument
from ..arguments import PublishArgument
from ..arguments import Types
from ..errors import AppStoreConnectError

AppStoreVersionLocalizationInfos = Union[
    List[AppStoreVersionLocalizationInfo],
    Types.AppStoreVersionLocalizationInfoArgument,
]
BetaBuildLocalizationsInfo = Union[
    List[BetaBuildInfo],
    Types.BetaBuildLocalizations,
]


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
    def get_build_pre_release_version(
            self,
            build_id: ResourceId,
            should_print: bool = True,
    ) -> PreReleaseVersion:
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

    @cli.action('app-store-version',
                BuildArgument.BUILD_ID_RESOURCE_ID,
                action_group=AppStoreConnectActionGroup.BUILDS)
    def get_build_app_store_version(
            self,
            build_id: ResourceId,
            should_print: bool = True,
    ) -> AppStoreVersion:
        """
        Get the App Store version of a specific build.
        """

        return self._get_related_resource(
            build_id,
            Build,
            AppStoreVersion,
            self.api_client.builds.read_app_store_version,
            should_print,
        )

    @cli.action(
        'add-beta-test-info',
        BuildArgument.BUILD_ID_RESOURCE_ID,
        *ArgumentGroups.ADD_BETA_TEST_INFO_OPTIONAL_ARGUMENTS,
        action_group=AppStoreConnectActionGroup.BUILDS)
    def add_beta_test_info(
            self,
            build_id: ResourceId,
            beta_build_localizations: Optional[BetaBuildLocalizationsInfo] = None,
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
        *ArgumentGroups.SUBMIT_TO_TESTFLIGHT_OPTIONAL_ARGUMENTS,
        action_group=AppStoreConnectActionGroup.BUILDS)
    def submit_to_testflight(
            self,
            build_id: ResourceId,
            max_build_processing_wait: Optional[Union[int, Types.MaxBuildProcessingWait]] = None,
    ) -> BetaAppReviewSubmission:
        """
        Submit build to TestFlight
        """

        max_processing_minutes = Types.MaxBuildProcessingWait.resolve_value(max_build_processing_wait)

        self.logger.info(Colors.BLUE(f'\nSubmit build {build_id!r} to TestFlight beta review'))

        try:
            build, app = self.api_client.builds.read_with_include(build_id, App)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error))

        try:
            self._assert_app_has_testflight_information(app)
        except ValueError as ve:
            raise AppStoreConnectError(str(ve)) from ve

        if max_processing_minutes:
            build = self.wait_until_build_is_processed(build, max_processing_minutes)

        return self.create_beta_app_review_submission(build.id)

    @cli.action(
        'submit-to-app-store',
        BuildArgument.BUILD_ID_RESOURCE_ID,
        *ArgumentGroups.SUBMIT_TO_APP_STORE_OPTIONAL_ARGUMENTS,
        action_group=AppStoreConnectActionGroup.BUILDS)
    def submit_to_app_store(
            self,
            build_id: ResourceId,
            max_build_processing_wait: Optional[Union[int, Types.MaxBuildProcessingWait]] = None,
            # App Store Version information arguments
            copyright: Optional[str] = None,
            earliest_release_date: Optional[Union[datetime, Types.EarliestReleaseDate]] = None,
            platform: Platform = AppStoreVersionArgument.PLATFORM.get_default(),
            release_type: Optional[ReleaseType] = None,
            version_string: Optional[str] = None,
            app_store_version_info: Optional[Union[AppStoreVersionInfo, Types.AppStoreVersionInfoArgument]] = None,
            # App Store Version Localization arguments
            description: Optional[str] = None,
            keywords: Optional[str] = None,
            locale: Optional[Locale] = None,
            marketing_url: Optional[str] = None,
            promotional_text: Optional[str] = None,
            support_url: Optional[str] = None,
            whats_new: Optional[Union[str, Types.WhatsNewArgument]] = None,
            app_store_version_localizations: Optional[AppStoreVersionLocalizationInfos] = None,
    ) -> AppStoreVersionSubmission:
        """
        Submit build to App Store review
        """
        app_store_version_info = self._get_app_store_version_info(
            app_store_version_info,
            copyright,
            earliest_release_date,
            platform,
            release_type,
            version_string,
        )
        app_store_version_localization_infos = self._get_app_store_version_localization_infos(
            app_store_version_localizations,
            description,
            keywords,
            locale,
            marketing_url,
            promotional_text,
            support_url,
            whats_new,
        )
        return self._submit_to_app_store(
            build_id,
            Types.MaxBuildProcessingWait.resolve_value(max_build_processing_wait),
            app_store_version_info,
            app_store_version_localization_infos,
        )

    def _submit_to_app_store(
        self,
        build_id: ResourceId,
        max_processing_minutes: int,
        app_store_version_info: AppStoreVersionInfo,
        app_store_version_localization_infos: List[AppStoreVersionLocalizationInfo],
    ) -> AppStoreVersionSubmission:
        self.logger.info(Colors.BLUE(f'\nSubmit build {build_id!r} to App Store review'))

        try:
            build, app = self.api_client.builds.read_with_include(build_id, App)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error))

        if max_processing_minutes:
            build = self.wait_until_build_is_processed(build, max_processing_minutes)

        if app_store_version_info.version_string is None:
            self.logger.info("\nVersion string is not specified. Obtain it from build's pre-release version...")
            pre_release_version = self.get_build_pre_release_version(build_id, should_print=False)
            app_store_version_info.version_string = pre_release_version.attributes.version

        self.logger.info(
            Colors.BLUE(f'\nUsing version {app_store_version_info.version_string} for App Store submission'),
        )

        app_store_version = self._ensure_app_store_version(app, build, app_store_version_info)
        self.echo('')

        self._create_or_update_app_store_version_localizations(
            app,
            app_store_version,
            app_store_version_localization_infos,
        )

        app_store_version_submission = self.create_app_store_version_submission(app_store_version.id)

        platform_slug = app_store_version_info.platform.value.lower().replace('_', '')
        submission_url = f'https://appstoreconnect.apple.com/apps/{app.id}/appstore/{platform_slug}/version/inflight'
        self.logger.info(f'\nCheck App Store submission details from\n{submission_url}\n')

        return app_store_version_submission

    def wait_until_build_is_processed(
        self,
        build: Build,
        max_processing_minutes: int,
        retry_wait_seconds: int = 30,
    ) -> Build:
        is_first_attempt = True
        start_waiting = time.time()
        while time.time() - start_waiting < max_processing_minutes * 60:
            if build.attributes.processingState is BuildProcessingState.PROCESSING:
                if is_first_attempt:
                    self._log_build_processing_message(build.id, max_processing_minutes)

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
                if not is_first_attempt:
                    self.logger.info(Colors.BLUE('Processing build %s is completed\n'), build.id)
                return build
            is_first_attempt = False

        raise IOError((
            f'Waiting for build {build.id} processing timed out in {max_processing_minutes} minutes. '
            f'You can configure maximum timeout using {PublishArgument.MAX_BUILD_PROCESSING_WAIT.flag} '
            f'command line option, or {Types.MaxBuildProcessingWait.environment_variable_key} environment variable.'
        ))

    def _log_build_processing_message(self, build_id: ResourceId, max_processing_minutes: int):
        processing_message_template = (
            '\n'
            'Processing of builds by Apple can take a while, '
            'the timeout for waiting the processing '
            'to finish for build %s is set to %d minutes.'
        )
        self.logger.info(Colors.BLUE(processing_message_template), build_id, max_processing_minutes)

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
            if beta_app_localization.attributes.locale is app.attributes.primaryLocale:
                return beta_app_localization
        # If nothing matches, then just take the first
        return beta_app_localizations[0] if beta_app_localizations else None

    def _ensure_app_store_version(
        self,
        app: App,
        build: Build,
        app_store_version_info: AppStoreVersionInfo,
    ) -> AppStoreVersion:
        app_store_version = self._get_editable_app_store_version(app, app_store_version_info.platform)
        if app_store_version is None:
            # Version does not exist, create a new version for App Store review submission
            self.logger.info(f'\n{AppStoreVersion} does not exist for build {build.id}')
            app_store_version = self.create_app_store_version(
                build.id,
                platform=app_store_version_info.platform,
                copyright=app_store_version_info.copyright,
                earliest_release_date=app_store_version_info.earliest_release_date,
                release_type=app_store_version_info.release_type,
                version_string=app_store_version_info.version_string,
            )
        else:
            self._update_existing_app_store_version(app_store_version, build, app_store_version_info)
        return app_store_version

    def _create_or_update_app_store_version_localizations(
        self,
        app: App,
        app_store_version: AppStoreVersion,
        app_store_version_localizations: List[AppStoreVersionLocalizationInfo],
    ):
        is_first_app_store_version = self._is_first_app_store_version(app, app_store_version.attributes.platform)
        existing_localizations = self._get_existing_app_store_version_localizations(app_store_version)
        for localization in app_store_version_localizations:
            if is_first_app_store_version:  # Release notes are not allowed for first releases
                localization.whats_new = None
            localization_id = existing_localizations.get(localization.locale or app.attributes.primaryLocale)

            try:
                self._create_or_update_app_store_version_localization(
                    localization_id,
                    app,
                    app_store_version,
                    localization,
                )
            except AppStoreConnectApiError as error:
                verb = 'update' if localization_id else 'create new'
                message = f'Failed to {verb} {AppStoreVersionLocalization} for locale {localization.locale}:'
                self.echo(f'{Colors.YELLOW(message)}\n{error}\n')

    def _create_or_update_app_store_version_localization(
            self,
            existing_localization_id: Optional[ResourceId],
            app: App,
            app_store_version: AppStoreVersion,
            localization: AppStoreVersionLocalizationInfo,
    ):
        if existing_localization_id is None:
            self.echo(Colors.GREEN(f'Create new {AppStoreVersionLocalization} for locale {localization.locale}'))
            app_store_version_localization = self.api_client.app_store_version_localizations.create(
                app_store_version,
                localization.locale or app.attributes.primaryLocale,  # Use app's primary locale if not defined
                description=localization.description,
                keywords=localization.keywords,
                marketing_url=localization.marketing_url,
                promotional_text=localization.promotional_text,
                support_url=localization.support_url,
                whats_new=localization.whats_new,
            )
        else:
            self.echo(Colors.GREEN(f'Update {AppStoreVersionLocalization} for locale {localization.locale}'))
            app_store_version_localization = self.api_client.app_store_version_localizations.modify(
                existing_localization_id,
                description=localization.description,
                keywords=localization.keywords,
                marketing_url=localization.marketing_url,
                promotional_text=localization.promotional_text,
                support_url=localization.support_url,
                whats_new=localization.whats_new,
            )
        self.printer.print_resource(app_store_version_localization, True)
        self.echo('')

    def _update_existing_app_store_version(
        self,
        app_store_version: AppStoreVersion,
        build: Build,
        app_store_version_info: AppStoreVersionInfo,
    ):
        self.logger.info((
            f'\nFound existing {AppStoreVersion} {app_store_version.id} '
            f'in state "{app_store_version.attributes.appStoreState}". '
        ))

        updates: Dict[str, str] = {'build': build.id}
        if app_store_version_info.copyright:
            updates['copyright'] = app_store_version_info.copyright
        if app_store_version_info.earliest_release_date:
            updates['earliest release date'] = AppStoreVersion.to_iso_8601(app_store_version_info.earliest_release_date)
        if app_store_version_info.release_type:
            updates['release type'] = app_store_version_info.release_type.value.lower()
        if app_store_version_info.version_string:
            updates['version string'] = app_store_version_info.version_string

        update_message = ', '.join(
            f'{param}: {shlex.quote(value)}'
            for param, value in updates.items()
        )
        self.logger.info(f'Use it for current submission by updating it with {update_message}.')

        return self.update_app_store_version(
            app_store_version.id,
            build_id=build.id,
            copyright=app_store_version_info.copyright,
            earliest_release_date=app_store_version_info.earliest_release_date,
            release_type=app_store_version_info.release_type,
            version_string=app_store_version_info.version_string,
        )

    def _is_first_app_store_version(self, app: App, platform: Platform) -> bool:
        versions_filter = self.api_client.app_store_versions.Filter(platform=platform)
        app_store_versions = self.api_client.apps.list_app_store_versions(
            app,
            resource_filter=versions_filter,
            limit=2,
        )
        return len(app_store_versions) < 2

    def _get_existing_app_store_version_localizations(
        self,
        app_store_version: AppStoreVersion,
    ) -> Dict[Locale, ResourceId]:
        localizations = self.api_client.app_store_versions.list_app_store_version_localizations(app_store_version)
        return {
            localization.attributes.locale: localization.id
            for localization in localizations
        }

    def _get_editable_app_store_version(self, app: App, platform: Platform) -> Optional[AppStoreVersion]:
        versions_filter = self.api_client.app_store_versions.Filter(
            app_store_state=AppStoreState.editable_states(),
            platform=platform,
        )
        app_store_versions = self.api_client.apps.list_app_store_versions(app, resource_filter=versions_filter)
        app_store_versions.sort(key=lambda asv: LooseVersion(asv.attributes.versionString))
        return app_store_versions[-1] if app_store_versions else None

    @classmethod
    def _get_app_store_version_info(
        cls,
        app_store_version_info_argument: Optional[Union[AppStoreVersionInfo, Types.AppStoreVersionInfoArgument]],
        copyright: Optional[str],
        earliest_release_date: Optional[Union[datetime, Types.EarliestReleaseDate]],
        platform: Platform,
        release_type: Optional[ReleaseType],
        version_string: Optional[str],
    ) -> AppStoreVersionInfo:
        if app_store_version_info_argument is None:
            app_store_version_info = AppStoreVersionInfo(platform=platform)
        elif isinstance(app_store_version_info_argument, Types.AppStoreVersionInfoArgument):
            app_store_version_info = app_store_version_info_argument.value
        else:
            app_store_version_info = app_store_version_info_argument

        if platform is not AppStoreVersionArgument.PLATFORM.get_default():
            # Platform has a default value when invoked from CLI,
            # override it only in case non-default value was provided
            app_store_version_info.platform = platform
        if copyright:
            app_store_version_info.copyright = copyright
        if earliest_release_date:
            if isinstance(earliest_release_date, Types.EarliestReleaseDate):
                app_store_version_info.earliest_release_date = earliest_release_date.value
            else:
                app_store_version_info.earliest_release_date = earliest_release_date
        if release_type:
            app_store_version_info.release_type = release_type
        if version_string:
            app_store_version_info.version_string = version_string
        return app_store_version_info

    @classmethod
    def _get_app_store_version_localization_infos(
        cls,
        app_store_version_localizations: Optional[AppStoreVersionLocalizationInfos],
        description: Optional[str],
        keywords: Optional[str],
        locale: Optional[Locale],
        marketing_url: Optional[str],
        promotional_text: Optional[str],
        support_url: Optional[str],
        whats_new: Optional[Union[str, Types.WhatsNewArgument]] = None,
    ) -> List[AppStoreVersionLocalizationInfo]:
        if isinstance(app_store_version_localizations, Types.AppStoreVersionLocalizationInfoArgument):
            app_store_version_localization_infos = app_store_version_localizations.value
        else:
            app_store_version_localization_infos = app_store_version_localizations or []

        app_store_version_localization_info = AppStoreVersionLocalizationInfo(
            description=description,
            keywords=keywords,
            locale=locale,
            marketing_url=marketing_url,
            promotional_text=promotional_text,
            support_url=support_url,
            whats_new=whats_new.value if isinstance(whats_new, Types.WhatsNewArgument) else whats_new,
        )
        if set(app_store_version_localization_info.__dict__.values()) != {None}:
            # At least some field is defined
            app_store_version_localization_infos.append(app_store_version_localization_info)

        return app_store_version_localization_infos
