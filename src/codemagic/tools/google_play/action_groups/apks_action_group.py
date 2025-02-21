from abc import ABCMeta
from pathlib import Path
from typing import List

from codemagic import cli
from codemagic.cli import Colors
from codemagic.google import GoogleError
from codemagic.google.resources.google_play import Apk
from codemagic.tools.google_play.action_groups.google_play_action_groups import GooglePlayActionGroups
from codemagic.tools.google_play.arguments import ApksArgument
from codemagic.tools.google_play.errors import GooglePlayError
from codemagic.tools.google_play.google_play_base_action import GooglePlayBaseAction


class ApksActionGroup(GooglePlayBaseAction, metaclass=ABCMeta):
    @cli.action(
        "list",
        action_group=GooglePlayActionGroups.APKS,
    )
    def list_apks(
        self,
        should_print: bool = True,
    ) -> List[Apk]:
        """
        List APKs from Google Play for an app
        """

        try:
            with self.using_app_edit() as edit:
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
        action_group=GooglePlayActionGroups.APKS,
    )
    def upload_apk(
        self,
        apk_path: Path,
        should_print: bool = True,
    ) -> Apk:
        """
        Upload APK at given path to Google Play
        """

        self.logger.info(Colors.GREEN(f'Upload APK "{apk_path}"'))

        try:
            with self.using_app_edit() as edit:
                apk = self.client.apks.upload(
                    self.package_name,
                    edit.id,
                    apk_path=apk_path,
                )
        except GoogleError as ge:
            error_message = f"Uploading APK {apk_path} to Google Play failed."
            self.logger.warning(Colors.RED(error_message))
            raise GooglePlayError(str(ge))

        self.printer.print_resource(apk, should_print=should_print)
        return apk
