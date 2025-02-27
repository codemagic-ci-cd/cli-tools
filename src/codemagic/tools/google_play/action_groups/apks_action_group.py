import pathlib
from abc import ABCMeta
from pathlib import Path
from typing import List
from typing import Optional
from typing import Union

from codemagic import cli
from codemagic.cli import Colors
from codemagic.google import GoogleError
from codemagic.google.resources.google_play import Apk
from codemagic.google.resources.google_play import AppEdit
from codemagic.google.resources.google_play import DeobfuscationFileType
from codemagic.google.resources.google_play import ExpansionFileType
from codemagic.google.resources.google_play import LocalizedText
from codemagic.models.application_package import ApkPackage
from codemagic.tools.google_play.action_groups.google_play_action_groups import GooglePlayActionGroups
from codemagic.tools.google_play.argument_types import ReleaseNotesArgument
from codemagic.tools.google_play.arguments import ApksArgument
from codemagic.tools.google_play.arguments import GooglePlayArgument
from codemagic.tools.google_play.arguments import ReleaseArgument
from codemagic.tools.google_play.arguments import TracksArgument
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
        apk_package: Optional[ApkPackage] = None,
        should_print: bool = True,
    ) -> Apk:
        """
        Upload APK at given path to Google Play
        """
        if apk_package is None:
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

        self.logger.info(Colors.GREEN(f"\nUploaded APK {apk_path} to Google Play"))
        self.printer.print_resource(apk, should_print=should_print)
        return apk

    @cli.action(
        "publish",
        ApksArgument.APK_PATH,
        TracksArgument.TRACK_NAME,
        ReleaseArgument.RELEASE_NAME,
        ReleaseArgument.IN_APP_UPDATE_PRIORITY,
        ReleaseArgument.STAGED_ROLLOUT_FRACTION,
        ReleaseArgument.SUBMIT_AS_DRAFT,
        ReleaseArgument.RELEASE_NOTES,
        ReleaseArgument.CHANGES_NOT_SENT_FOR_REVIEW,
        ApksArgument.PROGUARD_MAPPING_PATH,
        ApksArgument.MAIN_EXPANSION_FILE_PATH,
        ApksArgument.PATCH_EXPANSION_FILE_PATH,
        action_group=GooglePlayActionGroups.APKS,
    )
    def publish_apk(
        self,
        apk_path: Path,
        track_name: str,
        release_name: Optional[str] = None,
        in_app_update_priority: Optional[int] = None,
        staged_rollout_fraction: Optional[float] = None,
        submit_as_draft: Optional[bool] = None,
        release_notes: Optional[Union[ReleaseNotesArgument, List[LocalizedText]]] = None,
        changes_not_sent_for_review: Optional[bool] = None,
        proguard_mapping_path: Optional[pathlib.Path] = None,
        main_expansion_file_path: Optional[pathlib.Path] = None,
        patch_expansion_file_path: Optional[pathlib.Path] = None,
        should_print: bool = True,
    ):
        """
        Publish APK at given path to Google Play as a release to specified track
        """
        try:
            apk_package = ApkPackage(apk_path)
        except IOError:
            raise ApksArgument.APK_PATH.raise_argument_error("Not a valid APK")

        self.logger.info(Colors.BLUE(f'Publishing APK "{apk_path}" to Google Play track {track_name}\n'))

        package_name = apk_package.get_package_name()
        try:
            edit = self.client.edits.create(package_name)
            apk = self.upload_apk(
                apk_path,
                edit=edit,
                apk_package=apk_package,
                should_print=should_print,
            )

            if proguard_mapping_path:
                self.upload_deobfuscation_file(
                    package_name,
                    deobfuscation_file_path=proguard_mapping_path,
                    apk_version_code=apk.versionCode,
                    deobfuscation_file_type=DeobfuscationFileType.PROGUARD,
                    edit=edit,
                    should_print=should_print,
                )
            if main_expansion_file_path:
                self.upload_expansion_file(
                    package_name,
                    expansion_file_path=main_expansion_file_path,
                    apk_version_code=apk.versionCode,
                    expansion_file_type=ExpansionFileType.MAIN,
                    edit=edit,
                    should_print=should_print,
                )
            if patch_expansion_file_path:
                self.upload_expansion_file(
                    package_name,
                    expansion_file_path=patch_expansion_file_path,
                    apk_version_code=apk.versionCode,
                    expansion_file_type=ExpansionFileType.PATCH,
                    edit=edit,
                    should_print=should_print,
                )

            self.set_track_release(
                package_name=package_name,
                track_name=track_name,
                version_codes=[str(apk.versionCode)],
                release_name=release_name,
                in_app_update_priority=in_app_update_priority,
                staged_rollout_fraction=staged_rollout_fraction,
                submit_as_draft=submit_as_draft,
                release_notes=release_notes,
                changes_not_sent_for_review=changes_not_sent_for_review,
                edit=edit,
                should_print=should_print,
            )
        except GoogleError as ge:
            error_message = f'Publishing APK "{apk_path}" to track "{track_name}" failed.'
            self.logger.warning(Colors.RED(error_message))
            raise GooglePlayError(str(ge))

        self.logger.info(Colors.GREEN(f"Successfully published APK to Google Play track {track_name}"))
