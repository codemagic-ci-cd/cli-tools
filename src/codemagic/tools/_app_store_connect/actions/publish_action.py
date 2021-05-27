from __future__ import annotations

import pathlib
from abc import ABCMeta
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union

from codemagic import cli
from codemagic.apple.resources import Build
from codemagic.apple.resources import PreReleaseVersion
from codemagic.cli import Colors
from codemagic.models import Altool
from codemagic.models.application_package import Ipa
from codemagic.models.application_package import MacOsPackage

from ..abstract_base_action import AbstractBaseAction
from ..arguments import PublishArgument
from ..arguments import Types
from ..errors import AppStoreConnectError


class PublishAction(AbstractBaseAction, metaclass=ABCMeta):

    @cli.action('publish',
                PublishArgument.APPLICATION_PACKAGE_PATH_PATTERNS,
                PublishArgument.APPLE_ID,
                PublishArgument.APP_SPECIFIC_PASSWORD,
                PublishArgument.SUBMIT_TO_TESTFLIGHT,
                action_options={'requires_api_client': False})
    def publish(self,
                application_package_path_patterns: Sequence[pathlib.Path],
                apple_id: Optional[str] = None,
                app_specific_password: Optional[Types.AppSpecificPassword] = None,
                submit_to_testflight: Optional[bool] = None) -> None:
        """
        Publish application packages to App Store and submit them to Testflight
        """

        if not (apple_id and app_specific_password):
            self._assert_api_client_credentials(
                'Either Apple ID and app specific password or App Store Connect API key information is required.')
        elif submit_to_testflight:
            self._assert_api_client_credentials('It is required for submitting an app to Testflight.')

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

        failed_packages: List[str] = []
        for application_package in application_packages:
            try:
                build, pre_release_version = self._publish_application_package(altool, application_package)
                if submit_to_testflight:
                    self.create_beta_app_review_submission(build.id)
            except IOError as error:
                # TODO: Should we fail the whole action on first publishing failure?
                failed_packages.append(str(application_package.path))
                self.logger.error(Colors.RED(error.args[0]))

        if failed_packages:
            raise AppStoreConnectError(f'Failed to publish {", ".join(failed_packages)}')

    def _publish_application_package(
            self,
            altool: Altool,
            application_package: Union[Ipa, MacOsPackage]) -> Tuple[Build, PreReleaseVersion]:
        """
        :raises IOError in case any step of publishing fails
        """
        self.logger.info(Colors.BLUE('\nPublish "%s" to App Store Connect'), application_package.path)
        self.logger.info(application_package.get_text_summary())

        self._validate_artifact_with_altool(altool, application_package.path)
        self._upload_artifact_with_altool(altool, application_package.path)

        bundle_id = application_package.bundle_identifier
        self.logger.info(Colors.BLUE('\nFind application entry from App Store Connect for uploaded binary'))
        try:
            app = self.list_apps(bundle_id_identifier=bundle_id, should_print=False)[0]
        except IndexError:
            raise IOError(f'Did not find app with bundle identifier "{bundle_id}" from App Store Connect')
        else:
            self.printer.print_resource(app, True)

        self.logger.info(Colors.BLUE('\nFind freshly uploaded build'))
        for build in self.list_app_builds(app.id, should_print=False):
            if build.attributes.version == application_package.version_code:
                pre_release_version = self.get_build_pre_release_version(build.id, should_print=False)
                if pre_release_version.attributes.version == application_package.version:
                    break
        else:
            raise IOError(f'Did not find corresponding build from App Store versions for "{application_package.path}"')

        self.logger.info(Colors.GREEN('\nPublished build is'))
        self.printer.print_resource(build, True)
        self.printer.print_resource(pre_release_version, True)
        return build, pre_release_version

    def _get_publishing_application_packages(
            self,
            path_patterns: Sequence[pathlib.Path]) -> List[Union[Ipa, MacOsPackage]]:
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
        message = result.success_message or f'No errors validating archive at "{artifact_path}".'
        self.logger.info(Colors.GREEN(message))

    def _upload_artifact_with_altool(self, altool: Altool, artifact_path: pathlib.Path):
        self.logger.info(Colors.BLUE('\nUpload "%s" to App Store Connect'), artifact_path)
        result = altool.upload_app(artifact_path)
        message = result.success_message or f'No errors uploading "{artifact_path}".'
        self.logger.info(Colors.GREEN(message))
