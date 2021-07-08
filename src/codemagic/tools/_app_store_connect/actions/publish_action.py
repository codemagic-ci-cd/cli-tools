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
from codemagic.apple.resources import BetaAppLocalization
from codemagic.apple.resources import Build
from codemagic.apple.resources import BuildProcessingState
from codemagic.apple.resources import Locale
from codemagic.apple.resources import ResourceId
from codemagic.cli import Colors
from codemagic.models import Altool
from codemagic.models.application_package import Ipa
from codemagic.models.application_package import MacOsPackage

from ..abstract_base_action import AbstractBaseAction
from ..arguments import BetaBuildInfo
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
                skip_package_validation: Optional[bool] = None,
                max_build_processing_wait: Optional[Types.MaxBuildProcessingWait] = None) -> None:
        """
        Publish application packages to App Store and submit them to Testflight
        """

        # Workaround to support overriding default value by environment variable.
        if max_build_processing_wait:
            max_processing_minutes = max_build_processing_wait.value
        else:
            max_processing_minutes = Types.MaxBuildProcessingWait.default_value

        beta_build_infos = [*beta_build_localizations.value] if beta_build_localizations else []

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

        if whats_new:
            beta_build_infos.append(BetaBuildInfo(whats_new=whats_new.value, locale=locale))

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
                        beta_build_infos,
                        max_processing_minutes,
                    )
                else:
                    continue  # Cannot submit macOS packages to TestFlight, skip
            except (IOError, ValueError) as error:
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
        beta_build_infos: Sequence[BetaBuildInfo],
        max_processing_minutes: int,
    ):
        if not beta_build_infos and not submit_to_testflight:
            return  # Nothing to do with the ipa...

        app = self._get_uploaded_build_application(ipa)
        build = self._get_uploaded_build(app, ipa)

        if beta_build_infos:
            self._submit_beta_build_localization_infos(build, beta_build_infos)
        if submit_to_testflight:
            self._submit_build_to_testflight(build, app, max_processing_minutes)

    def _submit_beta_build_localization_infos(self, build: Build, beta_build_infos: Sequence[BetaBuildInfo]):
        self.logger.info(Colors.BLUE('\nUpdate beta build localization info in TestFlight for uploaded build'))
        for info in beta_build_infos:
            self.create_beta_build_localization(build_id=build.id, locale=info.locale, whats_new=info.whats_new)

    def _submit_build_to_testflight(self, build: Build, app: App, max_processing_minutes: int):
        self.logger.info(Colors.BLUE('\nSubmit uploaded build to TestFlight beta review'))
        self._assert_app_has_testflight_information(app)
        build = self._wait_until_build_is_processed(build, max_processing_minutes)
        self.create_beta_app_review_submission(build.id)

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
        try:
            found_builds = self.api_client.apps.list_builds(app_id)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error))

        for build in found_builds:
            if build.attributes.version == application_package.version_code:
                pre_release_version = self.api_client.builds.read_pre_release_version(build.id)
                if pre_release_version and pre_release_version.attributes.version == application_package.version:
                    return build

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

    def _get_uploaded_build_application(self, application_package: Union[Ipa, MacOsPackage]) -> App:
        bundle_id = application_package.bundle_identifier
        self.logger.info(Colors.BLUE('\nFind application entry from App Store Connect for uploaded binary'))
        try:
            app = self.list_apps(bundle_id_identifier=bundle_id, should_print=False)[0]
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

    def _get_app_default_beta_localization(self, app: App) -> Optional[BetaAppLocalization]:
        beta_app_localizations = self.api_client.apps.list_beta_app_localizations(app)
        for beta_app_localization in beta_app_localizations:
            if beta_app_localization.attributes.locale.value == app.attributes.primaryLocale:
                return beta_app_localization
        # If nothing matches, then just take the first
        return beta_app_localizations[0] if beta_app_localizations else None

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
