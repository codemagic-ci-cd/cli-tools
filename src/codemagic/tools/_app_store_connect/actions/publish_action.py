from __future__ import annotations

import pathlib
import time
from abc import ABCMeta
from typing import List
from typing import Optional
from typing import Sequence
from typing import Union

from codemagic import cli
from codemagic.apple import AppStoreConnectApiError
from codemagic.apple.resources import App
from codemagic.apple.resources import Build
from codemagic.apple.resources import Locale
from codemagic.apple.resources import ResourceId
from codemagic.cli import Colors
from codemagic.models import Altool
from codemagic.models.application_package import Ipa
from codemagic.models.application_package import MacOsPackage

from ..abstract_base_action import AbstractBaseAction
from ..arguments import BuildArgument
from ..arguments import PublishArgument
from ..arguments import Types
from ..errors import AppStoreConnectError


class PublishAction(AbstractBaseAction, metaclass=ABCMeta):

    @cli.action('publish',
                PublishArgument.APPLICATION_PACKAGE_PATH_PATTERNS,
                PublishArgument.APPLE_ID,
                PublishArgument.APP_SPECIFIC_PASSWORD,
                PublishArgument.SUBMIT_TO_TESTFLIGHT,
                BuildArgument.LOCALE_DEFAULT,
                BuildArgument.WHATS_NEW,
                BuildArgument.BETA_BUILD_LOCALIZATIONS,
                BuildArgument.BETA_GROUP_NAMES_OPTIONAL,
                PublishArgument.SKIP_PACKAGE_VALIDATION,
                PublishArgument.MAX_BUILD_PROCESSING_WAIT,
                action_options={'requires_api_client': False})
    def publish(self,
                application_package_path_patterns: Sequence[pathlib.Path],
                apple_id: Optional[str] = None,
                app_specific_password: Optional[Types.AppSpecificPassword] = None,
                submit_to_testflight: Optional[bool] = None,
                locale: Optional[Locale] = None,
                whats_new: Optional[Types.WhatsNewArgument] = None,
                beta_build_localizations: Optional[Types.BetaBuildLocalizations] = None,
                beta_group_names: Optional[List[str]] = None,
                skip_package_validation: Optional[bool] = None,
                max_build_processing_wait: Optional[Types.MaxBuildProcessingWait] = None) -> None:
        """
        Publish application packages to App Store, submit them to Testflight, and release to the groups of beta testers
        """

        if not (apple_id and app_specific_password):
            self._assert_api_client_credentials(
                'Either Apple ID and app specific password or App Store Connect API key information is required.')
        else:
            # Those need API key based authentication
            if submit_to_testflight:
                self._assert_api_client_credentials('It is required for submitting an app to Testflight.')
            if beta_build_localizations:
                self._assert_api_client_credentials(
                    "It is required for submitting localized beta test info for what's new in the uploaded build.")

        application_packages = self._get_publishing_application_packages(application_package_path_patterns)
        try:
            altool = Altool(
                username=apple_id,
                password=app_specific_password.value if app_specific_password else None,
                key_identifier=self._key_identifier,
                issuer_id=self._issuer_id,
                private_key=self._private_key,
            )
        except ValueError as ve:
            raise AppStoreConnectError(str(ve))

        validate_package = not bool(skip_package_validation)
        failed_packages: List[str] = []
        for application_package in application_packages:
            try:
                self._publish_application_package(altool, application_package, validate_package)
                if isinstance(application_package, Ipa):
                    self._handle_ipa_testflight_submission(
                        application_package,
                        submit_to_testflight,
                        beta_build_localizations,
                        locale,
                        whats_new,
                        max_build_processing_wait,
                        beta_group_names,
                    )
                else:
                    continue  # Cannot submit macOS packages to TestFlight, skip
            except (AppStoreConnectError, IOError, ValueError) as error:
                failed_packages.append(str(application_package.path))
                self.logger.error(Colors.RED(error.args[0]))

        if failed_packages:
            raise AppStoreConnectError(f'Failed to publish {", ".join(failed_packages)}')

    def _publish_application_package(
            self, altool: Altool, application_package: Union[Ipa, MacOsPackage], validate_package: bool):
        """
        :raises IOError in case any step of publishing fails
        """
        self.logger.info(Colors.BLUE('\nPublish "%s" to App Store Connect'), application_package.path)
        self.logger.info(application_package.get_text_summary())
        if validate_package:
            self._validate_artifact_with_altool(altool, application_package.path)
        else:
            self.logger.info(Colors.YELLOW('\nSkip validating "%s" for App Store Connect'), application_package.path)
        self._upload_artifact_with_altool(altool, application_package.path)

    def _handle_ipa_testflight_submission(
        self,
        ipa: Ipa,
        submit_to_testflight: Optional[bool],
        beta_build_localizations: Optional[Types.BetaBuildLocalizations],
        locale: Optional[Locale],
        whats_new: Optional[Types.WhatsNewArgument],
        max_build_processing_wait: Optional[Types.MaxBuildProcessingWait],
        beta_group_names: Optional[List[str]],
    ):
        if not beta_build_localizations and not whats_new and not submit_to_testflight and not beta_group_names:
            return  # Nothing to do with the ipa...

        app = self._get_uploaded_build_application(ipa)
        build = self._get_uploaded_build(app, ipa)

        if beta_build_localizations or whats_new:
            self.add_beta_test_info(build.id, beta_build_localizations, locale, whats_new)
        if submit_to_testflight:
            self.submit_to_testflight(build.id, max_build_processing_wait)
        if submit_to_testflight and beta_group_names:
            self.add_build_to_beta_groups(build.id, beta_group_names)

    def _find_build(
        self,
        app_id: ResourceId,
        application_package: Union[Ipa, MacOsPackage],
        retries: int = 20,
        retry_wait_seconds: int = 30,
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
        )
        try:
            found_builds = self.api_client.builds.list(builds_filter)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error))

        if found_builds:
            return found_builds[0]

        # Matching build was not found.
        if retries > 0:
            # There are retries left, wait a bit and try again.
            self.logger.info(
                (
                    'Build has finished uploading but is processing on App Store Connect side. Could not find the '
                    'build matching the uploaded version yet. Waiting %d seconds to try again, %d attempts remaining.'
                ),
                retry_wait_seconds,
                retries,
            )
            time.sleep(retry_wait_seconds)
            return self._find_build(
                app_id, application_package, retries=retries - 1, retry_wait_seconds=retry_wait_seconds)
        else:
            # There are no more retries left, give up.
            raise IOError(
                'The build was successfully uploaded to App Store Connect but processing the corresponding artifact '
                f'"{application_package.path}" by Apple took longer than expected. Further actions like updating the '
                'What to test information or submitting the build to beta review could not be performed at the moment '
                'but can be completed manually in TestFlight once the build has finished processing.')

    def _get_uploaded_build_application(self, application_package: Union[Ipa, MacOsPackage]) -> App:
        bundle_id = application_package.bundle_identifier
        self.logger.info(Colors.BLUE('\nFind application entry from App Store Connect for uploaded binary'))
        try:
            app = self.list_apps(
                bundle_id_identifier=bundle_id, bundle_id_identifier_strict_match=True, should_print=False)[0]
        except IndexError:
            raise IOError(f'Did not find app with bundle identifier "{bundle_id}" from App Store Connect')
        else:
            self.printer.print_resource(app, True)
        return app

    def _get_uploaded_build(
            self, app: App, application_package: Union[Ipa, MacOsPackage]) -> Build:
        self.logger.info(Colors.BLUE('\nFind uploaded build'))
        build = self._find_build(app.id, application_package)
        self.logger.info(Colors.GREEN('\nUploaded build is'))
        self.printer.print_resource(build, True)
        return build

    def _get_publishing_application_packages(
            self, path_patterns: Sequence[pathlib.Path]) -> List[Union[Ipa, MacOsPackage]]:
        _path_patterns = list(path_patterns)
        if len(_path_patterns) == 1 and _path_patterns[0].exists():
            # Add exempt for single path that exists to avoid unnecessary log output
            found_application_paths = [_path_patterns[0]]
        else:
            found_application_paths = list(self.find_paths(*path_patterns))

        application_packages: List[Union[Ipa, MacOsPackage]] = []
        for path in found_application_paths:
            if path.suffix == '.ipa':
                application_package: Union[Ipa, MacOsPackage] = Ipa(path)
            elif path.suffix == '.pkg':
                application_package = MacOsPackage(path)
            else:
                raise AppStoreConnectError(f'Unsupported package type for App Store Connect publishing: {path}')

            try:
                application_package.get_summary()
            except FileNotFoundError as fnf:
                message = f'Invalid package for App Store Connect publishing: {fnf.args[0]} not found from {path}'
                self.logger.warning(Colors.YELLOW(message))
            except (ValueError, IOError) as error:
                message = f'Unable to process package {path} for App Store Connect publishing: {error.args[0]}'
                self.logger.warning(Colors.YELLOW(message))
            else:
                application_packages.append(application_package)

        if not application_packages:
            patterns = ', '.join(f'"{pattern}"' for pattern in path_patterns)
            raise AppStoreConnectError(f'No application packages found for patterns {patterns}')
        return application_packages

    def _validate_artifact_with_altool(self, altool: Altool, artifact_path: pathlib.Path):
        self.logger.info(Colors.BLUE('\nValidate "%s" for App Store Connect'), artifact_path)
        result = altool.validate_app(artifact_path)
        message = result.success_message if result else f'No errors validating archive at "{artifact_path}".'
        self.logger.info(Colors.GREEN(message))

    def _upload_artifact_with_altool(self, altool: Altool, artifact_path: pathlib.Path):
        self.logger.info(Colors.BLUE('\nUpload "%s" to App Store Connect'), artifact_path)
        result = altool.upload_app(artifact_path)
        message = result.success_message if result else f'No errors uploading "{artifact_path}".'
        self.logger.info(Colors.GREEN(message))
