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
                BuildArgument.LOCALE_OPTIONAL_WITH_DEFAULT,
                BuildArgument.WHATS_NEW,
                PublishArgument.SKIP_PACKAGE_VALIDATION,
                action_options={'requires_api_client': False})
    def publish(self,
                application_package_path_patterns: Sequence[pathlib.Path],
                apple_id: Optional[str] = None,
                app_specific_password: Optional[Types.AppSpecificPassword] = None,
                submit_to_testflight: Optional[bool] = None,
                locale: Locale = BuildArgument.LOCALE_OPTIONAL_WITH_DEFAULT.get_default(),
                whats_new: Optional[Types.WhatsNewArgument] = None,
                skip_package_validation: Optional[bool] = None) -> None:
        """
        Publish application packages to App Store and submit them to Testflight
        """

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
                    build, pre_release_version = self._get_uploaded_build(application_package)
                    self.create_beta_app_review_submission(build.id)
                    if locale and whats_new:
                        self.create_beta_build_localization(build.id, locale, whats_new)
            except IOError as error:
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
        for build in self.list_app_builds(app_id, should_print=False):
            if build.attributes.version == application_package.version_code:
                pre_release_version = self.get_build_pre_release_version(build.id, should_print=False)
                if pre_release_version.attributes.version == application_package.version:
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

    def _wait_until_build_is_processed(self, build: Build, retries: int = 20, retry_wait_seconds: int = 30) -> Build:
        if build.attributes.processingState is BuildProcessingState.PROCESSING:
            self.logger.info(
                'Build %s is still being processed, wait %d seconds and check again', build.id, retry_wait_seconds)
            if retries > 0:
                time.sleep(retry_wait_seconds)
                return self._wait_until_build_is_processed(
                    self.get_build(build.id, should_print=False),
                    retries=retries-1,
                    retry_wait_seconds=retry_wait_seconds,
                )
            else:
                raise IOError(f'Waiting for build {build.id} processing timed out')
        elif build.attributes.processingState in (BuildProcessingState.FAILED, BuildProcessingState.INVALID):
            raise IOError(f'Uploaded build {build.id} is {build.attributes.processingState.value.lower()}')
        else:
            self.logger.info(Colors.BLUE('Processing build %s is completed'), build.id)
            return build

    def _get_uploaded_build(self, application_package: Union[Ipa, MacOsPackage]) -> Tuple[Build, PreReleaseVersion]:
        bundle_id = application_package.bundle_identifier
        self.logger.info(Colors.BLUE('\nFind application entry from App Store Connect for uploaded binary'))
        try:
            app = self.list_apps(bundle_id_identifier=bundle_id, should_print=False)[0]
        except IndexError:
            raise IOError(f'Did not find app with bundle identifier "{bundle_id}" from App Store Connect')
        else:
            self.printer.print_resource(app, True)

        self.logger.info(Colors.BLUE('\nFind freshly uploaded build'))
        build, pre_release_version = self._find_build(app.id, application_package)
        build = self._wait_until_build_is_processed(build)
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
