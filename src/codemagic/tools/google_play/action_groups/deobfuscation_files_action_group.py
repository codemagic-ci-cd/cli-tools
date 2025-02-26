import pathlib
from abc import ABCMeta
from typing import Optional

from codemagic import cli
from codemagic.cli import Colors
from codemagic.google import GoogleError
from codemagic.google.resources.google_play import AppEdit
from codemagic.google.resources.google_play import DeobfuscationFile
from codemagic.google.resources.google_play import DeobfuscationFileType
from codemagic.tools.google_play.action_groups.google_play_action_groups import GooglePlayActionGroups
from codemagic.tools.google_play.arguments import ApksArgument
from codemagic.tools.google_play.arguments import DeobfuscationsArgument
from codemagic.tools.google_play.arguments import GooglePlayArgument
from codemagic.tools.google_play.errors import GooglePlayError
from codemagic.tools.google_play.google_play_base_action import GooglePlayBaseAction


class DeobfuscationFilesActionGroup(GooglePlayBaseAction, metaclass=ABCMeta):
    @cli.action(
        "upload",
        GooglePlayArgument.PACKAGE_NAME,
        DeobfuscationsArgument.DEOBFUSCATION_FILE_PATH,
        ApksArgument.APK_VERSION_CODE,
        DeobfuscationsArgument.DEOBFUSCATION_FILE_TYPE,
        action_group=GooglePlayActionGroups.DEOBFUSCATION_FILES,
    )
    def upload_deobfuscation_file(
        self,
        package_name: str,
        deobfuscation_file_path: pathlib.Path,
        apk_version_code: int,
        deobfuscation_file_type: DeobfuscationFileType = DeobfuscationsArgument.DEOBFUSCATION_FILE_TYPE.get_default(),
        edit: Optional[AppEdit] = None,
        should_print: bool = True,
    ) -> DeobfuscationFile:
        """
        Upload a new deobfuscation file and attach it to the specified APK.
        """

        upload_message = f'Upload {deobfuscation_file_type} deobfuscation file "{deobfuscation_file_path}'
        self.logger.info(Colors.BLUE(upload_message))
        try:
            with self.using_app_edit(package_name, edit) as edit:
                deobfuscation_file = self.client.deobfuscation_files.upload(
                    package_name,
                    edit.id,
                    apk_version_code=apk_version_code,
                    deobfuscation_file_path=deobfuscation_file_path,
                    deobfuscation_file_type=deobfuscation_file_type,
                )
        except GoogleError as ge:
            error_message = f"Uploading deobfuscation file {deobfuscation_file_path} to Google Play failed."
            self.logger.warning(Colors.RED(error_message))
            raise GooglePlayError(str(ge))

        self.logger.info(Colors.GREEN(f"\nUploaded {deobfuscation_file_type} deobfuscation file"))
        self.printer.print_resource(deobfuscation_file, should_print=should_print)
        return deobfuscation_file
