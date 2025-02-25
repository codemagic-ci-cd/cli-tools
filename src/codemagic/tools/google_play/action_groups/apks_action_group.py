import pathlib
from abc import ABCMeta
from pathlib import Path
from typing import List
from typing import Optional

from codemagic import cli
from codemagic.cli import Colors
from codemagic.google import GoogleError
from codemagic.google.resources.google_play import Apk
from codemagic.google.resources.google_play import AppEdit
from codemagic.google.resources.google_play import DeobfuscationFile
from codemagic.google.resources.google_play import DeobfuscationFileType
from codemagic.tools.google_play.action_groups.google_play_action_groups import GooglePlayActionGroups
from codemagic.tools.google_play.arguments import ApksArgument
from codemagic.tools.google_play.arguments import ProguardMapArgument
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

        self.logger.info(Colors.BLUE(f'Upload APK "{apk_path}"'))

        try:
            with self.using_app_edit(edit) as edit:
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

    @cli.action(
        "upload-proguard-map",
        ProguardMapArgument.PROGUARD_MAP_PATH,
        ApksArgument.VERSION_CODE,
        action_group=GooglePlayActionGroups.APKS,
    )
    def upload_proguard_map(
        self,
        proguard_map_path: pathlib.Path,
        apk_version_code: int,
        edit: Optional[AppEdit] = None,
        should_print: bool = True,
    ) -> DeobfuscationFile:
        """
        Upload a new ProGuard mapping deobfuscation file and attach it to the specified APK.
        """

        self.logger.info(Colors.BLUE(f'Upload ProGuard mapping "{proguard_map_path}'))
        try:
            with self.using_app_edit(edit) as edit:
                deobfuscation_file = self.client.deobfuscation_files.upload(
                    self.package_name,
                    edit.id,
                    apk_version_code=apk_version_code,
                    deobfuscation_file_path=proguard_map_path,
                    deobfuscation_file_type=DeobfuscationFileType.PROGUARD,
                )
        except GoogleError as ge:
            error_message = f"Uploading ProGuard mapping {proguard_map_path} to Google Play failed."
            self.logger.warning(Colors.RED(error_message))
            raise GooglePlayError(str(ge))

        self.printer.print_resource(deobfuscation_file, should_print=should_print)
        return deobfuscation_file
