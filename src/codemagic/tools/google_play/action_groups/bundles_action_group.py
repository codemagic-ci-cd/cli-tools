from abc import ABCMeta
from pathlib import Path
from typing import List
from typing import Optional
from typing import Union

from codemagic import cli
from codemagic.cli import Colors
from codemagic.google import GoogleError
from codemagic.google.resources.google_play import AppEdit
from codemagic.google.resources.google_play import Bundle
from codemagic.google.resources.google_play import LocalizedText
from codemagic.models.application_package import AabPackage
from codemagic.tools.google_play.action_groups.google_play_action_groups import GooglePlayActionGroups
from codemagic.tools.google_play.argument_types import ReleaseNotesArgument
from codemagic.tools.google_play.arguments import BundlesArgument
from codemagic.tools.google_play.arguments import GooglePlayArgument
from codemagic.tools.google_play.arguments import ReleaseArgument
from codemagic.tools.google_play.arguments import TracksArgument
from codemagic.tools.google_play.errors import GooglePlayError
from codemagic.tools.google_play.google_play_base_action import GooglePlayBaseAction


class BundlesActionGroup(GooglePlayBaseAction, metaclass=ABCMeta):
    @cli.action(
        "list",
        GooglePlayArgument.PACKAGE_NAME,
        action_group=GooglePlayActionGroups.BUNDLES,
    )
    def list_bundles(
        self,
        package_name: str,
        edit: Optional[AppEdit] = None,
        should_print: bool = True,
    ) -> List[Bundle]:
        """
        List App Bundles from Google Play for an app
        """

        try:
            with self.using_app_edit(package_name, edit) as edit:
                bundles = self.client.bundles.list(package_name, edit.id)
        except GoogleError as ge:
            error_message = f'Listing App Bundles from Google Play for package "{package_name}" failed.'
            self.logger.warning(Colors.RED(error_message))
            raise GooglePlayError(str(ge))

        if not bundles:
            self.logger.warning(Colors.YELLOW(f'No App Bundles found for package "{package_name}"'))
        else:
            self.logger.info(Colors.GREEN(f'Found {len(bundles)} App Bundles for package "{package_name}"'))
        self.printer.print_resources(bundles, should_print)

        return bundles

    @cli.action(
        "upload",
        BundlesArgument.BUNDLE_PATH,
        action_group=GooglePlayActionGroups.BUNDLES,
    )
    def upload_bundle(
        self,
        bundle_path: Path,
        edit: Optional[AppEdit] = None,
        aab_package: Optional[AabPackage] = None,
        should_print: bool = True,
    ) -> Bundle:
        """
        Upload App Bundle at given path to Google Play
        """
        if aab_package is None:
            try:
                aab_package = AabPackage(bundle_path)
            except IOError:
                raise BundlesArgument.BUNDLE_PATH.raise_argument_error("Not a valid App Bundle")

        self.logger.info(Colors.BLUE(f'Upload App Bundle "{bundle_path}" to Google Play'))
        self.logger.info(aab_package.get_text_summary())

        package_name = aab_package.get_package_name()
        try:
            with self.using_app_edit(package_name, edit) as edit:
                bundle = self.client.bundles.upload(
                    package_name,
                    edit.id,
                    bundle_path=bundle_path,
                )
        except GoogleError as ge:
            error_message = f"Uploading App Bundle {bundle_path} to Google Play failed."
            self.logger.warning(Colors.RED(error_message))
            raise GooglePlayError(str(ge))

        self.logger.info(Colors.GREEN(f"\nUploaded App Bundle {bundle_path} to Google Play"))
        self.printer.print_resource(bundle, should_print=should_print)
        return bundle

    @cli.action(
        "publish",
        BundlesArgument.BUNDLE_PATH,
        TracksArgument.TRACK_NAME,
        ReleaseArgument.RELEASE_NAME,
        ReleaseArgument.IN_APP_UPDATE_PRIORITY,
        ReleaseArgument.STAGED_ROLLOUT_FRACTION,
        ReleaseArgument.SUBMIT_AS_DRAFT,
        ReleaseArgument.RELEASE_NOTES,
        ReleaseArgument.CHANGES_NOT_SENT_FOR_REVIEW,
        action_group=GooglePlayActionGroups.BUNDLES,
    )
    def publish_bundle(
        self,
        bundle_path: Path,
        track_name: str,
        release_name: Optional[str] = None,
        in_app_update_priority: Optional[int] = None,
        staged_rollout_fraction: Optional[float] = None,
        submit_as_draft: Optional[bool] = None,
        release_notes: Optional[Union[ReleaseNotesArgument, List[LocalizedText]]] = None,
        changes_not_sent_for_review: Optional[bool] = None,
        should_print: bool = True,
    ):
        """
        Publish App Bundle at given path to Google Play as a release to specified track
        """
        try:
            aab_package = AabPackage(bundle_path)
        except IOError:
            raise BundlesArgument.BUNDLE_PATH.raise_argument_error("Not a valid App Bundle")

        self.logger.info(Colors.BLUE(f'Publishing App Bundle "{bundle_path}" to Google Play track {track_name}\n'))

        package_name = aab_package.get_package_name()
        try:
            edit = self.client.edits.create(package_name)
            bundle = self.upload_bundle(
                bundle_path,
                edit=edit,
                aab_package=aab_package,
                should_print=should_print,
            )
            self.set_track_release(
                package_name=package_name,
                track_name=track_name,
                version_codes=[str(bundle.versionCode)],
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
            error_message = f'Publishing App Bundle "{bundle_path}" to track "{track_name}" failed.'
            self.logger.warning(Colors.RED(error_message))
            raise GooglePlayError(str(ge))

        self.logger.info(Colors.GREEN(f"\nSuccessfully published App Bundle to Google Play track {track_name}"))
