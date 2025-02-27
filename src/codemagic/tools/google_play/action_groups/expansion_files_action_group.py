import pathlib
from abc import ABCMeta
from typing import Optional

from codemagic import cli
from codemagic.cli import Colors
from codemagic.google import GoogleError
from codemagic.google.resources.google_play import AppEdit
from codemagic.google.resources.google_play import ExpansionFile
from codemagic.google.resources.google_play import ExpansionFileType
from codemagic.tools.google_play.action_groups.google_play_action_groups import GooglePlayActionGroups
from codemagic.tools.google_play.arguments import ApksArgument
from codemagic.tools.google_play.arguments import ExpansionFileArgument
from codemagic.tools.google_play.arguments import GooglePlayArgument
from codemagic.tools.google_play.errors import GooglePlayError
from codemagic.tools.google_play.google_play_base_action import GooglePlayBaseAction


class ExpansionFilesActionGroup(GooglePlayBaseAction, metaclass=ABCMeta):
    @cli.action(
        "upload",
        GooglePlayArgument.PACKAGE_NAME,
        ExpansionFileArgument.EXPANSION_FILE_PATH,
        ApksArgument.APK_VERSION_CODE,
        ExpansionFileArgument.EXPANSION_FILE_TYPE,
        action_group=GooglePlayActionGroups.EXPANSION_FILES,
    )
    def upload_expansion_file(
        self,
        package_name: str,
        expansion_file_path: pathlib.Path,
        apk_version_code: int,
        expansion_file_type: ExpansionFileType = ExpansionFileArgument.EXPANSION_FILE_TYPE.get_default(),
        edit: Optional[AppEdit] = None,
        should_print: bool = True,
    ) -> ExpansionFile:
        """
        Upload a new expansion file and attach it to the specified APK.
        """

        self.logger.info(Colors.BLUE(f'Upload {expansion_file_type} expansion file "{expansion_file_path}'))
        try:
            with self.using_app_edit(package_name, edit) as edit:
                expansion_file = self.client.expansion_files.upload(
                    package_name,
                    edit.id,
                    apk_version_code=apk_version_code,
                    expansion_file_path=expansion_file_path,
                    expansion_file_type=expansion_file_type,
                )
        except GoogleError as ge:
            error_message = f"Uploading expansion file {expansion_file_path} to Google Play failed."
            self.logger.warning(Colors.RED(error_message))
            raise GooglePlayError(str(ge))

        self.logger.info(Colors.GREEN(f"\nUploaded {expansion_file_type} expansion file {expansion_file_path}"))
        self.printer.print_resource(expansion_file, should_print=should_print)
        return expansion_file

    @cli.action(
        "reference",
        GooglePlayArgument.PACKAGE_NAME,
        ApksArgument.APK_VERSION_CODE,
        ExpansionFileArgument.EXPANSION_FILE_TYPE,
        ExpansionFileArgument.REFERENCES_APK_VERSION_CODE,
        action_group=GooglePlayActionGroups.EXPANSION_FILES,
    )
    def reference_expansion_file(
        self,
        package_name: str,
        apk_version_code: int,
        references_apk_version_code: int,
        expansion_file_type: ExpansionFileType = ExpansionFileArgument.EXPANSION_FILE_TYPE.get_default(),
        edit: Optional[AppEdit] = None,
        should_print: bool = True,
    ) -> ExpansionFile:
        """
        Update the APK's expansion file configuration to reference another APK's expansion file.
        """

        message = (
            f"Update APK {apk_version_code} {expansion_file_type} expansion file configuration to reference "
            f"APK {references_apk_version_code} expansion file"
        )
        self.logger.info(Colors.BLUE(message))
        try:
            with self.using_app_edit(package_name, edit) as edit:
                expansion_file = self.client.expansion_files.update(
                    package_name,
                    edit.id,
                    apk_version_code=apk_version_code,
                    expansion_file_type=expansion_file_type,
                    references_version=references_apk_version_code,
                )
        except GoogleError as ge:
            error_message = f"Updating {expansion_file_type} expansion file in Google Play failed."
            self.logger.warning(Colors.RED(error_message))
            raise GooglePlayError(str(ge))

        self.logger.info(Colors.GREEN(f"\nUpdated {expansion_file_type} expansion file"))
        self.printer.print_resource(expansion_file, should_print=should_print)
        return expansion_file
