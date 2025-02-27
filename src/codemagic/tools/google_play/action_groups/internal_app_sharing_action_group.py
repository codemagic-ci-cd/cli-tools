import pathlib
from abc import ABCMeta
from typing import Optional

from codemagic import cli
from codemagic.cli import Colors
from codemagic.google import GoogleError
from codemagic.google.resources.google_play import InternalAppSharingArtifact
from codemagic.models.application_package import AabPackage
from codemagic.models.application_package import ApkPackage
from codemagic.tools.google_play.action_groups.google_play_action_groups import GooglePlayActionGroups
from codemagic.tools.google_play.arguments import ApksArgument
from codemagic.tools.google_play.arguments import BundlesArgument
from codemagic.tools.google_play.errors import GooglePlayError
from codemagic.tools.google_play.google_play_base_action import GooglePlayBaseAction


class InternalAppSharingActionGroup(GooglePlayBaseAction, metaclass=ABCMeta):
    @cli.action(
        "upload",
        ApksArgument.APK_PATH_MUTUALLY_EXCLUSIVE,
        BundlesArgument.BUNDLE_PATH_MUTUALLY_EXCLUSIVE,
        action_group=GooglePlayActionGroups.INTERNAL_APP_SHARING,
    )
    def upload_to_internal_app_sharing(
        self,
        apk_path: Optional[pathlib.Path] = None,
        bundle_path: Optional[pathlib.Path] = None,
        should_print: bool = True,
    ) -> InternalAppSharingArtifact:
        """
        Upload APK or App Bundle to Google Play through Internal App Sharing
        to get a link that can be shared with your team
        """
        if apk_path is not None:
            return self.upload_apk_to_internal_app_sharing(apk_path, should_print=should_print)
        elif bundle_path is not None:
            return self.upload_bundle_to_internal_app_sharing(bundle_path, should_print=should_print)
        else:
            raise GooglePlayError("Either APK or App Bundle path is required")

    @cli.action(
        "upload-apk",
        ApksArgument.APK_PATH,
        action_group=GooglePlayActionGroups.INTERNAL_APP_SHARING,
    )
    def upload_apk_to_internal_app_sharing(
        self,
        apk_path: pathlib.Path,
        should_print: bool = True,
    ) -> InternalAppSharingArtifact:
        """
        Upload APK to Google Play through Internal App Sharing
        to get a link that can be shared with your team
        """
        try:
            apk_package = ApkPackage(apk_path)
        except IOError:
            raise ApksArgument.APK_PATH.raise_argument_error("Not a valid APK")

        self.logger.info(Colors.BLUE(f'Upload APK "{apk_path}" to Google Play internal app sharing'))
        self.logger.info(apk_package.get_text_summary())

        try:
            internal_app_sharing_artifact = self.client.internal_app_sharing_artifacts.upload_apk(
                apk_package.get_package_name(),
                apk_path=apk_path,
            )
        except GoogleError as ge:
            error_message = f"Uploading APK {apk_path} to Google Play failed."
            self.logger.warning(Colors.RED(error_message))
            raise GooglePlayError(str(ge))

        self.logger.info(Colors.GREEN("\nUploaded APK to Google Play internal app sharing"))
        self.printer.print_resource(internal_app_sharing_artifact, should_print=should_print)
        return internal_app_sharing_artifact

    @cli.action(
        "upload-bundle",
        BundlesArgument.BUNDLE_PATH,
        action_group=GooglePlayActionGroups.INTERNAL_APP_SHARING,
    )
    def upload_bundle_to_internal_app_sharing(
        self,
        bundle_path: pathlib.Path,
        should_print: bool = True,
    ) -> InternalAppSharingArtifact:
        """
        Upload App Bundle to Google Play through Internal App Sharing
        to get a link that can be shared with your team
        """
        try:
            aab_package = AabPackage(bundle_path)
        except IOError:
            raise BundlesArgument.BUNDLE_PATH.raise_argument_error("Not a valid App Bundle")

        self.logger.info(Colors.BLUE(f'Upload App Bundle "{bundle_path}" to Google Play internal app sharing'))
        self.logger.info(aab_package.get_text_summary())

        try:
            internal_app_sharing_artifact = self.client.internal_app_sharing_artifacts.upload_bundle(
                aab_package.get_package_name(),
                bundle_path=bundle_path,
            )
        except GoogleError as ge:
            error_message = f"Uploading App Bundle {bundle_path} to Google Play failed."
            self.logger.warning(Colors.RED(error_message))
            raise GooglePlayError(str(ge))

        self.logger.info(Colors.GREEN("\nUploaded App Bundle to Google Play internal app sharing"))
        self.printer.print_resource(internal_app_sharing_artifact, should_print=should_print)
        return internal_app_sharing_artifact
