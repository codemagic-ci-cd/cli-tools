from __future__ import annotations

import pathlib
import time
from abc import ABCMeta
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union

from codemagic import cli
from codemagic.apple import AppStoreConnectApiError
from codemagic.apple.resources import App
from codemagic.apple.resources import Build
from codemagic.apple.resources import BuildProcessingState
from codemagic.apple.resources import Locale
from codemagic.apple.resources import PreReleaseVersion
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

        if not (apple_id and app_specific_password):
            self._assert_api_client_credentials(
                'Either Apple ID and app specific password or App Store Connect API key information is required.')
        elif submit_to_testflight:
            self._assert_api_client_credentials('It is required for submitting an app to Testflight.')

        if whats_new and not submit_to_testflight:
            raise BuildArgument.WHATS_NEW.raise_argument_error(
                f'{PublishArgument.SUBMIT_TO_TESTFLIGHT.flag} is required for submitting notes')

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
                if submit_to_testflight:
                    if isinstance(application_package, Ipa):
                        self._submit_build_to_testflight(application_package, locale, whats_new, max_processing_minutes)
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

    def _submit_build_to_testflight(
        self,
        ipa: Ipa,
        locale: Optional[Locale],
        whats_new: Optional[Types.WhatsNewArgument],
        max_processing_minutes: int,
    ):
        self.logger.info(Colors.BLUE('\nSubmit %s to TestFlight'), ipa.path)
        app = self._get_uploaded_build_application(ipa)
        build, pre_release_version = self._get_uploaded_build(app, ipa)

        if whats_new:
            self.create_beta_build_localization(build.id, locale, whats_new)

        self._assert_app_has_testflight_information(app)
        build = self._wait_until_build_is_processed(build, max_processing_minutes)
        self.create_beta_app_review_submission(build.id)

    def _find_build(
        self,
        app_id: ResourceId,
        application_package: Union[Ipa, MacOsPackage],
        retries: int = 10,
        retry_wait_seconds: int = 30,
    ) -> Tuple[Build, PreReleaseVersion]:
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
                    return build, pre_release_version

        # Matching build was not found.
        if retries > 0:
            # There are retries left, wait a bit and try again.
            self.logger.info(
                (
                    'Did not find build matching uploaded version yet, it might be still processing. '
                    'Waiting %d seconds to try again'
                ),
                retry_wait_seconds,
            )
            time.sleep(retry_wait_seconds)
            return self._find_build(
                app_id, application_package, retries=retries-1, retry_wait_seconds=retry_wait_seconds)
        else:
            # There are no more retries left, give up.
            raise IOError(f'Did not find corresponding build from App Store versions for "{application_package.path}"')

    def _wait_until_build_is_processed(
        self,
        build: Build,
        max_processing_minutes: int,
        retry_wait_seconds: int = 30,
    ) -> Build:
        self.logger.info(Colors.BLUE('\nWait until processing build %s is completed'), build.id)

        start_waiting = time.time()
        while time.time() - start_waiting < max_processing_minutes * 60:
            if build.attributes.processingState is BuildProcessingState.PROCESSING:
                msg_template = 'Build %s is still being processed, wait %d seconds and check again'
                self.logger.info(msg_template, build.id, retry_wait_seconds)
                time.sleep(retry_wait_seconds)
                try:
                    build = self.api_client.builds.read(build)
                except AppStoreConnectApiError as api_error:
                    raise AppStoreConnectError(str(api_error))
            elif build.attributes.processingState in (BuildProcessingState.FAILED, BuildProcessingState.INVALID):
                raise IOError(f'Uploaded build {build.id} is {build.attributes.processingState.value.lower()}')
            else:
                self.logger.info(Colors.BLUE('Processing build %s is completed'), build.id)
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
            self, app: App, application_package: Union[Ipa, MacOsPackage]) -> Tuple[Build, PreReleaseVersion]:
        self.logger.info(Colors.BLUE('\nFind freshly uploaded build'))
        build, pre_release_version = self._find_build(app.id, application_package)
        self.logger.info(Colors.GREEN('\nPublished build is'))
        self.printer.print_resource(build, True)
        self.printer.print_resource(pre_release_version, True)
        return build, pre_release_version

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

    def _get_missing_beta_app_information(self, app: App) -> List[str]:
        beta_app_localizations = self.api_client.apps.list_beta_app_localizations(app)
        default_beta_app_localization = beta_app_localizations[0]
        required_test_information = {
            'Feedback Email': default_beta_app_localization.attributes.feedbackEmail,
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
