from abc import ABCMeta
from pathlib import Path
from typing import List
from typing import Optional

from codemagic import cli
from codemagic.cli import Colors
from codemagic.google import GoogleError
from codemagic.google.resources.google_play import Apk
from codemagic.google.resources.google_play import AppEdit
from codemagic.google.resources.google_play import InternalAppSharingArtifact
from codemagic.models.application_package import ApkPackage
from codemagic.tools.google_play.action_groups.google_play_action_groups import GooglePlayActionGroups
from codemagic.tools.google_play.arguments import ApksArgument
from codemagic.tools.google_play.arguments import InternalAppSharingArgument
from codemagic.tools.google_play.errors import GooglePlayError
from codemagic.tools.google_play.google_play_base_action import GooglePlayBaseAction


class ApksActionGroup(GooglePlayBaseAction, metaclass=ABCMeta):
    @cli.action(
        "list",
        action_group=GooglePlayActionGroups.APKS,
    )
    def list_apks(
        self,
        edit: Optional[AppEdit] = None,
        should_print: bool = True,
    ) -> List[Apk]:
        """
        List APKs from Google Play for an app
        """

        try:
            with self.using_app_edit(edit) as edit:
                apks = self.client.apks.list(self.package_name, edit.id)
        except GoogleError as ge:
            error_message = f'Listing APKS from Google Play for package "{self.package_name}" failed.'
            self.logger.warning(Colors.RED(error_message))
            raise GooglePlayError(str(ge))

        if not apks:
            self.logger.warning(Colors.YELLOW(f'No APKs found for package "{self.package_name}"'))
        self.printer.print_resources(apks, should_print)

        return apks

    @cli.action(
        "upload",
        ApksArgument.APK_PATH,
        InternalAppSharingArgument.INTERNAL_APP_SHARING,
        action_group=GooglePlayActionGroups.APKS,
    )
    def upload_apk(
        self,
        apk_path: Path,
        internal_app_sharing: Optional[bool] = None,
        edit: Optional[AppEdit] = None,
        should_print: bool = True,
    ) -> Apk | InternalAppSharingArtifact:
        """
        Upload APK at given path to Google Play
        """

        if edit and internal_app_sharing:
            raise ValueError("Cannot use App edit to upload APK to internal app sharing")

        try:
            apk = ApkPackage(apk_path)
        except IOError:
            raise ApksArgument.APK_PATH.raise_argument_error("Not a valid APK file")

        if internal_app_sharing:
            self.logger.info(Colors.BLUE(f'Upload APK "{apk_path}" through internal app sharing'))
        else:
            self.logger.info(Colors.BLUE(f'Upload APK "{apk_path}"'))
        self.logger.info(apk.get_text_summary())

        uploaded_artifact: Apk | InternalAppSharingArtifact
        try:
            if internal_app_sharing:
                uploaded_artifact = self.client.internal_app_sharing_artifacts.upload_apk(
                    self.package_name,
                    apk_path=apk_path,
                )
            else:
                with self.using_app_edit(edit) as edit:
                    uploaded_artifact = self.client.apks.upload(
                        self.package_name,
                        edit.id,
                        apk_path=apk_path,
                    )
        except GoogleError as ge:
            error_message = f"Uploading APK {apk_path} to Google Play failed."
            self.logger.warning(Colors.RED(error_message))
            raise GooglePlayError(str(ge))

        self.printer.print_resource(uploaded_artifact, should_print=should_print)
        return uploaded_artifact
