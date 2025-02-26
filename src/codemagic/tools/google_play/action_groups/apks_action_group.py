from abc import ABCMeta
from pathlib import Path
from typing import List
from typing import Optional

from codemagic import cli
from codemagic.cli import Colors
from codemagic.google import GoogleError
from codemagic.google.resources.google_play import Apk
from codemagic.google.resources.google_play import AppEdit
from codemagic.models.application_package import ApkPackage
from codemagic.tools.google_play.action_groups.google_play_action_groups import GooglePlayActionGroups
from codemagic.tools.google_play.arguments import ApksArgument
from codemagic.tools.google_play.arguments import GooglePlayArgument
from codemagic.tools.google_play.errors import GooglePlayError
from codemagic.tools.google_play.google_play_base_action import GooglePlayBaseAction


class ApksActionGroup(GooglePlayBaseAction, metaclass=ABCMeta):
    @cli.action(
        "list",
        GooglePlayArgument.PACKAGE_NAME,
        action_group=GooglePlayActionGroups.APKS,
    )
    def list_apks(
        self,
        package_name: str,
        edit: Optional[AppEdit] = None,
        should_print: bool = True,
    ) -> List[Apk]:
        """
        List APKs from Google Play for an app
        """

        try:
            with self.using_app_edit(package_name, edit) as edit:
                apks = self.client.apks.list(package_name, edit.id)
        except GoogleError as ge:
            error_message = f'Listing APKS from Google Play for package "{package_name}" failed.'
            self.logger.warning(Colors.RED(error_message))
            raise GooglePlayError(str(ge))

        if not apks:
            self.logger.warning(Colors.YELLOW(f'No APKs found for package "{package_name}"'))
        self.printer.print_resources(apks, should_print)

        return apks

    @cli.action(
        "upload",
        ApksArgument.APK_PATH,
        action_group=GooglePlayActionGroups.APKS,
    )
    def upload_apk(
        self,
        apk_path: Path,
        edit: Optional[AppEdit] = None,
        should_print: bool = True,
    ) -> Apk:
        """
        Upload APK at given path to Google Play
        """
        try:
            apk_package = ApkPackage(apk_path)
        except IOError:
            raise ApksArgument.APK_PATH.raise_argument_error("Not a valid APK")

        self.logger.info(Colors.BLUE(f'Upload APK "{apk_path}" to Google Play'))
        self.logger.info(apk_package.get_text_summary())

        package_name = apk_package.get_package_name()
        try:
            with self.using_app_edit(package_name, edit) as edit:
                apk = self.client.apks.upload(
                    package_name,
                    edit.id,
                    apk_path=apk_path,
                )
        except GoogleError as ge:
            error_message = f"Uploading APK {apk_path} to Google Play failed."
            self.logger.warning(Colors.RED(error_message))
            raise GooglePlayError(str(ge))

        self.printer.print_resource(apk, should_print=should_print)
        return apk
