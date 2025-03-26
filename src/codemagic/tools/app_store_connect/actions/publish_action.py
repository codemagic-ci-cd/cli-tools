from __future__ import annotations

import dataclasses
import itertools
import pathlib
import time
from abc import ABCMeta
from dataclasses import dataclass
from datetime import datetime
from typing import List
from typing import Optional
from typing import Sequence
from typing import Union

from codemagic import cli
from codemagic.apple import AppStoreConnectApiError
from codemagic.apple.resources import App
from codemagic.apple.resources import Build
from codemagic.apple.resources import Locale
from codemagic.apple.resources import Platform
from codemagic.apple.resources import ReleaseType
from codemagic.apple.resources import ResourceId
from codemagic.cli import Argument
from codemagic.cli import Colors
from codemagic.models import Altool
from codemagic.models.application_package import Ipa
from codemagic.models.application_package import MacOsPackage

from ..abstract_base_action import AbstractBaseAction
from ..arguments import AppStoreVersionArgument
from ..arguments import AppStoreVersionInfo
from ..arguments import AppStoreVersionLocalizationArgument
from ..arguments import AppStoreVersionLocalizationInfo
from ..arguments import ArgumentGroups
from ..arguments import BuildArgument
from ..arguments import PublishArgument
from ..arguments import Types
from ..errors import AppStoreConnectError

AppStoreVersionLocalizationInfos = Union[
    List[AppStoreVersionLocalizationInfo],
    Types.AppStoreVersionLocalizationInfoArgument,
]


@dataclass
class AddBetaTestInfoOptions:
    beta_build_localizations: Optional[Types.BetaBuildLocalizations] = None
    locale: Optional[Locale] = None
    whats_new: Optional[Union[str, Types.WhatsNewArgument]] = None


@dataclass
class AddBuildToBetaGroupOptions:
    beta_group_names: List[str]


@dataclass
class SubmitToTestFlightOptions:
    expire_build_submitted_for_review: bool


@dataclass
class SubmitToAppStoreOptions:
    cancel_previous_submissions: bool
    # App Store Version information arguments
    copyright: Optional[str] = None
    earliest_release_date: Optional[datetime] = None
    platform: Platform = AppStoreVersionArgument.PLATFORM.get_default()
    release_type: Optional[ReleaseType] = None
    version_string: Optional[str] = None
    app_store_version_info: Optional[AppStoreVersionInfo] = None
    # App Store Version Localization arguments
    description: Optional[str] = None
    keywords: Optional[str] = None
    locale: Optional[Locale] = None
    marketing_url: Optional[str] = None
    promotional_text: Optional[str] = None
    support_url: Optional[str] = None
    whats_new: Optional[str] = None
    app_store_version_localizations: Optional[List[AppStoreVersionLocalizationInfo]] = None
    # App Store Version Phased Release arguments
    enable_phased_release: Optional[bool] = None
    disable_phased_release: Optional[bool] = None


ACTION_ARGUMENTS = (
    PublishArgument.APPLICATION_PACKAGE_PATH_PATTERNS,
    PublishArgument.APPLE_ID,
    PublishArgument.APP_SPECIFIC_PASSWORD,
    *ArgumentGroups.PACKAGE_UPLOAD_ARGUMENTS,
    PublishArgument.MAX_BUILD_FIND_WAIT,
    PublishArgument.MAX_BUILD_PROCESSING_WAIT,
    *PublishArgument.with_custom_argument_group(
        "add localized What's new (what to test) information to uploaded build",
        *ArgumentGroups.ADD_BETA_TEST_INFO_OPTIONAL_ARGUMENTS,
        exclude=(
            BuildArgument.LOCALE_DEFAULT,
            BuildArgument.WHATS_NEW,
        ),
    ),
    *PublishArgument.with_custom_argument_group(
        "submit build to TestFlight for beta review",
        PublishArgument.SUBMIT_TO_TESTFLIGHT,
        *ArgumentGroups.SUBMIT_TO_TESTFLIGHT_OPTIONAL_ARGUMENTS,
    ),
    *PublishArgument.with_custom_argument_group(
        "add build to Beta groups",
        *ArgumentGroups.ADD_BUILD_TO_BETA_GROUPS_OPTIONAL_ARGUMENTS,
    ),
    *PublishArgument.with_custom_argument_group(
        "submit build to App Store review",
        PublishArgument.SUBMIT_TO_APP_STORE,
        AppStoreVersionArgument.PLATFORM_OPTIONAL,
        *ArgumentGroups.SUBMIT_TO_APP_STORE_OPTIONAL_ARGUMENTS,
        exclude=(
            AppStoreVersionArgument.PLATFORM,
            AppStoreVersionLocalizationArgument.LOCALE_DEFAULT,
            AppStoreVersionLocalizationArgument.WHATS_NEW,
        ),
    ),
    *PublishArgument.with_custom_argument_group(
        "add localized meta information about build for TestFlight or App Store review submission",
        PublishArgument.LOCALE_DEFAULT,
        PublishArgument.WHATS_NEW,
    ),
    *PublishArgument.with_custom_argument_group(
        "set Apple's altool configuration options",
        *ArgumentGroups.ALTOOL_CONFIGURATION_ARGUMENTS,
    ),
)


class PublishAction(AbstractBaseAction, metaclass=ABCMeta):
    def _validate_publishing_arguments(
        self,
        apple_id: Optional[str] = None,
        app_specific_password: Optional[Types.AppSpecificPassword] = None,
        submit_to_testflight: Optional[bool] = None,
        submit_to_app_store: Optional[bool] = None,
        beta_build_localizations: Optional[Types.BetaBuildLocalizations] = None,
        enable_phased_release: Optional[bool] = None,
        disable_phased_release: Optional[bool] = None,
        **_other_args,
    ) -> None:
        if not (apple_id and app_specific_password):
            self._assert_api_client_credentials(
                "Either Apple ID and app specific password or App Store Connect API key information is required.",
            )
        else:
            # Those need API key based authentication
            if submit_to_testflight:
                self._assert_api_client_credentials("It is required for submitting an app to Testflight.")
            if beta_build_localizations:
                self._assert_api_client_credentials(
                    "It is required for submitting localized beta test info for what's new in the uploaded build.",
                )
            if submit_to_app_store:
                self._assert_api_client_credentials("It is required for submitting an app to App Store review.")

        try:
            Argument.resolve_optional_two_way_switch(enable_phased_release, disable_phased_release)
        except ValueError:
            enable_argument = AppStoreVersionArgument.ENABLE_PHASED_RELEASE
            disable_argument = AppStoreVersionArgument.DISABLE_PHASED_RELEASE
            raise AppStoreVersionArgument.ENABLE_PHASED_RELEASE.raise_argument_error(
                f'Using mutually exclusive switches "{enable_argument.flag}" and "{disable_argument.flag}".',
            )

    def _get_altool(
        self,
        apple_id: Optional[str] = None,
        app_specific_password: Optional[Types.AppSpecificPassword] = None,
        altool_verbose_logging: Optional[bool] = None,
    ) -> Altool:
        try:
            return Altool(
                username=apple_id,
                password=app_specific_password.value if app_specific_password else None,
                key_identifier=self._key_identifier,
                issuer_id=self._issuer_id,
                private_key=self._private_key,
                verbose=bool(altool_verbose_logging),
            )
        except ValueError as ve:
            raise AppStoreConnectError(str(ve))

    @classmethod
    def _get_app_store_connect_submit_options(
        cls,
        application_package: Union[Ipa, MacOsPackage],
        submit_to_testflight: Optional[bool],
        submit_to_app_store: Optional[bool],
        # Submit to TestFlight arguments
        expire_build_submitted_for_review: bool = False,
        # Beta test info arguments
        beta_build_localizations: Optional[Types.BetaBuildLocalizations] = None,
        locale: Optional[Locale] = None,
        whats_new: Optional[Union[Types.WhatsNewArgument, str]] = None,
        # Add build to beta group arguments
        beta_group_names: Optional[List[str]] = None,
        # Submit to App Store arguments
        copyright: Optional[str] = None,
        earliest_release_date: Optional[Union[datetime, Types.EarliestReleaseDate]] = None,
        platform: Optional[Platform] = None,
        release_type: Optional[ReleaseType] = None,
        version_string: Optional[str] = None,
        app_store_version_info: Optional[Union[AppStoreVersionInfo, Types.AppStoreVersionInfoArgument]] = None,
        cancel_previous_submissions: bool = False,
        # App Store Version Localization arguments
        description: Optional[str] = None,
        keywords: Optional[str] = None,
        marketing_url: Optional[str] = None,
        promotional_text: Optional[str] = None,
        support_url: Optional[str] = None,
        app_store_version_localizations: Optional[AppStoreVersionLocalizationInfos] = None,
        # App Store Version Phased Release arguments
        enable_phased_release: Optional[bool] = None,
        disable_phased_release: Optional[bool] = None,
    ):
        submit_to_testflight_options = None
        submit_to_app_store_options = None
        add_build_to_beta_group_options = None
        add_beta_test_info_options = None

        if not platform:
            platform = cls._get_application_package_platform(application_package)

        if submit_to_testflight:
            submit_to_testflight_options = SubmitToTestFlightOptions(
                expire_build_submitted_for_review=expire_build_submitted_for_review,
            )
        if submit_to_app_store:
            if isinstance(earliest_release_date, Types.EarliestReleaseDate):
                earliest_release_date = earliest_release_date.value
            if isinstance(app_store_version_info, Types.AppStoreVersionInfoArgument):
                app_store_version_info = app_store_version_info.value
            if isinstance(app_store_version_localizations, Types.AppStoreVersionLocalizationInfoArgument):
                app_store_version_localizations = app_store_version_localizations.value
            submit_to_app_store_options = SubmitToAppStoreOptions(
                cancel_previous_submissions=cancel_previous_submissions,
                # Non localized app metadata
                copyright=copyright,
                earliest_release_date=earliest_release_date,
                platform=platform,
                release_type=release_type,
                version_string=version_string,
                app_store_version_info=app_store_version_info,
                # Localized app metadata
                description=description,
                keywords=keywords,
                locale=locale,
                marketing_url=marketing_url,
                promotional_text=promotional_text,
                support_url=support_url,
                whats_new=whats_new.value if isinstance(whats_new, Types.WhatsNewArgument) else whats_new,
                app_store_version_localizations=app_store_version_localizations,
                # App Store Version Phased Release arguments
                enable_phased_release=enable_phased_release,
                disable_phased_release=disable_phased_release,
            )
        if beta_group_names:
            # Only builds submitted to TestFlight can be added to beta groups
            add_build_to_beta_group_options = AddBuildToBetaGroupOptions(
                beta_group_names=beta_group_names,
            )
        if beta_build_localizations or whats_new:
            add_beta_test_info_options = AddBetaTestInfoOptions(
                beta_build_localizations=beta_build_localizations,
                locale=locale,
                whats_new=whats_new,
            )

        return (
            submit_to_testflight_options,
            submit_to_app_store_options,
            add_beta_test_info_options,
            add_build_to_beta_group_options,
        )

    @staticmethod
    def _get_application_package_platform(application_package: Union[Ipa, MacOsPackage]) -> Platform:
        if isinstance(application_package, MacOsPackage):
            return Platform.MAC_OS
        if application_package.is_for_tvos():
            return Platform.TV_OS
        return Platform.IOS

    @cli.action(
        "publish",
        *ACTION_ARGUMENTS,
        action_options={"requires_api_client": False},
    )
    def publish(
        self,
        application_package_path_patterns: Sequence[pathlib.Path],
        apple_id: Optional[str] = None,
        app_specific_password: Optional[Types.AppSpecificPassword] = None,
        submit_to_testflight: Optional[bool] = None,
        submit_to_app_store: Optional[bool] = None,
        # Package upload and validation arguments
        skip_package_validation: Optional[bool] = None,  # Deprecated
        enable_package_validation: Optional[bool] = None,
        skip_package_upload: Optional[bool] = None,
        altool_retries_count: Optional[Types.AltoolRetriesCount] = None,
        altool_retry_wait: Optional[Types.AltoolRetryWait] = None,
        altool_verbose_logging: Optional[bool] = None,
        max_find_build_wait: Union[Types.MaxFindBuildWait, int] = PublishArgument.MAX_BUILD_FIND_WAIT.get_default(),
        max_build_processing_wait: Optional[Union[Types.MaxBuildProcessingWait, int]] = None,
        **app_store_connect_submit_options,
    ) -> None:
        """
        Publish application packages to App Store, submit them to Testflight, and release to the groups of beta testers
        """
        if bool(skip_package_validation):
            self._log_skip_validation_deprecation()

        self._validate_publishing_arguments(
            apple_id,
            app_specific_password,
            submit_to_testflight,
            submit_to_app_store,
            **app_store_connect_submit_options,
        )

        application_packages = self._get_publishing_application_packages(application_package_path_patterns)
        altool = self._get_altool(apple_id, app_specific_password, altool_verbose_logging)
        failed_packages: List[str] = []

        for application_package in application_packages:
            try:
                self._publish_application_package(
                    altool,
                    application_package,
                    enable_package_validation,
                    skip_package_upload,
                    Types.AltoolRetriesCount.resolve_value(altool_retries_count),
                    Types.AltoolRetryWait.resolve_value(altool_retry_wait),
                )
                self._process_application_after_upload(
                    application_package,
                    Types.MaxFindBuildWait.resolve_value(max_find_build_wait),
                    Types.MaxBuildProcessingWait.resolve_value(max_build_processing_wait),
                    *self._get_app_store_connect_submit_options(
                        application_package,
                        submit_to_testflight,
                        submit_to_app_store,
                        **app_store_connect_submit_options,
                    ),
                )
            except (AppStoreConnectError, IOError, ValueError) as error:
                failed_packages.append(str(application_package.path))
                self.logger.error(Colors.RED(error.args[0]))

        if failed_packages:
            raise AppStoreConnectError(f"Failed to publish {', '.join(failed_packages)}")

    def _log_skip_validation_deprecation(self):
        flag = PublishArgument.SKIP_PACKAGE_VALIDATION.flag
        message = (
            f"{Colors.YELLOW('Deprecation warning!')} Support for {Colors.WHITE(flag)} is deprecated"
            "and this flag will be removed in future releases."
            "\n"
            f"Starting from version 0.14.0 package validation "
            f"is disabled by default and using {Colors.WHITE(flag)} has no effect."
        )
        self.logger.info(message)

    def _publish_application_package(
        self,
        altool: Altool,
        application_package: Union[Ipa, MacOsPackage],
        enable_package_validation: Optional[bool],
        skip_package_upload: Optional[bool],
        altool_retries: int,
        altool_retry_wait: float,
    ):
        """
        :raises IOError in case any step of publishing fails
        """
        self.logger.info(Colors.BLUE('\nPublish "%s" to App Store Connect'), application_package.path)
        self.logger.info(application_package.get_text_summary())

        if bool(enable_package_validation):
            self._validate_artifact_with_altool(altool, application_package.path, altool_retries, altool_retry_wait)

        if not bool(skip_package_upload):
            self._upload_artifact_with_altool(altool, application_package.path, altool_retries, altool_retry_wait)
        else:
            self.logger.info(Colors.YELLOW('\nSkip uploading "%s" to App Store Connect'), application_package.path)

    def _process_application_after_upload(
        self,
        application_package: Union[Ipa, MacOsPackage],
        max_find_build_wait: int,
        max_build_processing_wait: int,
        testflight_options: Optional[SubmitToTestFlightOptions],
        app_store_options: Optional[SubmitToAppStoreOptions],
        beta_test_info_options: Optional[AddBetaTestInfoOptions],
        beta_group_options: Optional[AddBuildToBetaGroupOptions],
    ) -> None:
        if not any([testflight_options, app_store_options, beta_test_info_options, beta_group_options]):
            return  # Nothing to do with the application...

        app = self._get_uploaded_build_application(application_package)
        build = self._get_uploaded_build(app, application_package, max_find_build_wait)

        if beta_test_info_options:
            self.add_beta_test_info(
                build.id,
                beta_build_localizations=beta_test_info_options.beta_build_localizations,
                locale=beta_test_info_options.locale,
                whats_new=beta_test_info_options.whats_new,
            )

        if testflight_options or app_store_options or beta_group_options:
            self.wait_until_build_is_processed(build, max_build_processing_wait)

        if beta_group_options:
            self.add_build_to_beta_groups(
                build.id,
                beta_group_names=beta_group_options.beta_group_names,
            )

        if testflight_options:
            # Overwrite waiting since we already waited above.
            self.submit_to_testflight(
                build.id,
                max_build_processing_wait=0,
                expire_build_submitted_for_review=testflight_options.expire_build_submitted_for_review,
            )

        if app_store_options:
            if not app_store_options.version_string:
                app_store_options = dataclasses.replace(
                    app_store_options,
                    version_string=application_package.version,
                )
            self.submit_to_app_store(
                build.id,
                max_build_processing_wait=0,
                cancel_previous_submissions=app_store_options.cancel_previous_submissions,
                # App Store Version information arguments
                copyright=app_store_options.copyright,
                earliest_release_date=app_store_options.earliest_release_date,
                platform=app_store_options.platform,
                release_type=app_store_options.release_type,
                version_string=app_store_options.version_string,
                app_store_version_info=app_store_options.app_store_version_info,
                # App Store Version Localization arguments
                description=app_store_options.description,
                keywords=app_store_options.keywords,
                locale=app_store_options.locale,
                marketing_url=app_store_options.marketing_url,
                promotional_text=app_store_options.promotional_text,
                support_url=app_store_options.support_url,
                whats_new=app_store_options.whats_new,
                app_store_version_localizations=app_store_options.app_store_version_localizations,
                # App Store Version Phased Release arguments
                enable_phased_release=app_store_options.enable_phased_release,
                disable_phased_release=app_store_options.disable_phased_release,
            )

    def _find_build(
        self,
        app_id: ResourceId,
        application_package: Union[Ipa, MacOsPackage],
        max_find_build_minutes: int,
        retry_wait_seconds: int,
    ) -> Build:
        """
        Find corresponding build for the uploaded ipa or macOS package.
        Take into account that sometimes the build is not immediately available
        after the upload and as a result the API calls may not return it. Implement a
        simple retrying logic to overcome this issue.
        """
        builds_filter = self.api_client.builds.Filter(
            app=app_id,
            version=application_package.version_code,
            pre_release_version_version=application_package.version,
            pre_release_version_platform=self._get_application_package_platform(application_package),
        )

        not_found_message = "Could not find the build matching the uploaded version"
        default_retry_message = f"{not_found_message}, waiting {retry_wait_seconds} seconds to try again."
        first_retry_message = (
            f"Build has finished uploading but is not available in App Store Connect yet. "
            f"{default_retry_message} Timeout in {max_find_build_minutes} minutes."
        )

        find_started_at = time.time()
        for attempt in itertools.count():
            try:
                found_builds = self.api_client.builds.list(
                    builds_filter,
                    ordering=self.api_client.builds.Ordering.UPLOADED_DATE,
                    reverse=True,
                )
            except AppStoreConnectApiError as api_error:
                raise AppStoreConnectError(str(api_error))

            if found_builds:
                return found_builds[0]
            elif int(time.time() - find_started_at) <= max_find_build_minutes * 60:
                self.logger.info(first_retry_message if attempt == 0 else default_retry_message)
                time.sleep(retry_wait_seconds)
            else:
                self.logger.info(f"{not_found_message}. Timeout reached, stop trying.\n")
                break  # No more time left, give up.

        error_message = (
            "The build was successfully uploaded to App Store Connect but processing the corresponding artifact "
            f'"{application_package.path}" by Apple took longer than expected. Further actions like updating the '
            '"What to test information" or submitting the build to beta review could not be performed at the moment '
            "but can be completed manually in TestFlight once the build has finished processing.\n"
            f"You can configure maximum timeout using {PublishArgument.MAX_BUILD_FIND_WAIT.flag} "
            f"command line option, or {Types.MaxFindBuildWait.environment_variable_key} environment variable."
        )
        raise IOError(error_message)

    def _get_uploaded_build_application(self, application_package: Union[Ipa, MacOsPackage]) -> App:
        bundle_id = application_package.bundle_identifier
        self.logger.info(Colors.BLUE("\nFind application entry from App Store Connect for uploaded binary"))
        apps = self.list_apps(
            bundle_id_identifier=bundle_id,
            bundle_id_identifier_strict_match=True,
            should_print=False,
        )
        try:
            app = apps[0]
        except IndexError:
            raise IOError(f'Did not find app with bundle identifier "{bundle_id}" from App Store Connect')
        self.printer.print_resource(app, True)
        return app

    def _get_uploaded_build(
        self,
        app: App,
        application_package: Union[Ipa, MacOsPackage],
        max_find_build_minutes: int,
        retry_wait_seconds: int = 30,
    ) -> Build:
        self.logger.info(Colors.BLUE("\nFind uploaded build"))
        build = self._find_build(
            app.id,
            application_package,
            max_find_build_minutes,
            retry_wait_seconds,
        )
        self.logger.info(Colors.GREEN("\nUploaded build is"))
        self.printer.print_resource(build, True)
        return build

    def _get_publishing_application_packages(
        self,
        path_patterns: Sequence[pathlib.Path],
    ) -> List[Union[Ipa, MacOsPackage]]:
        _path_patterns = list(path_patterns)
        if len(_path_patterns) == 1 and _path_patterns[0].exists():
            # Add exempt for single path that exists to avoid unnecessary log output
            found_application_paths = [_path_patterns[0]]
        else:
            found_application_paths = list(self.find_paths(*path_patterns))

        application_packages: List[Union[Ipa, MacOsPackage]] = []
        for path in found_application_paths:
            if path.suffix == ".ipa":
                application_package: Union[Ipa, MacOsPackage] = Ipa(path)
            elif path.suffix == ".pkg":
                application_package = MacOsPackage(path)
            else:
                raise AppStoreConnectError(f"Unsupported package type for App Store Connect publishing: {path}")

            try:
                application_package.get_summary()
            except FileNotFoundError as fnf:
                message = f"Invalid package for App Store Connect publishing: {fnf.args[0]} not found from {path}"
                self.logger.warning(Colors.YELLOW(message))
            except (ValueError, IOError) as error:
                message = f"Unable to process package {path} for App Store Connect publishing: {error.args[0]}"
                self.logger.warning(Colors.YELLOW(message))
            else:
                application_packages.append(application_package)

        if not application_packages:
            patterns = ", ".join(f'"{pattern}"' for pattern in path_patterns)
            raise AppStoreConnectError(f"No application packages found for patterns {patterns}")
        return application_packages

    def _validate_artifact_with_altool(
        self,
        altool: Altool,
        artifact_path: pathlib.Path,
        retries: int,
        retry_wait: float,
    ):
        self.logger.info(Colors.BLUE('\nValidate "%s" for App Store Connect'), artifact_path)
        result = altool.validate_app(artifact_path, retries=retries, retry_wait_seconds=retry_wait)
        message = result.success_message if result else f'No errors validating archive at "{artifact_path}".'
        self.logger.info(Colors.GREEN(message))

    def _upload_artifact_with_altool(
        self,
        altool: Altool,
        artifact_path: pathlib.Path,
        retries: int,
        retry_wait: float,
    ):
        self.logger.info(Colors.BLUE('\nUpload "%s" to App Store Connect'), artifact_path)
        result = altool.upload_app(artifact_path, retries=retries, retry_wait_seconds=retry_wait)
        message = result.success_message if result else f'No errors uploading "{artifact_path}".'
        self.logger.info(Colors.GREEN(message))
