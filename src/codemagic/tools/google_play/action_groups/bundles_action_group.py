from abc import ABCMeta
from pathlib import Path
from typing import List

from codemagic import cli
from codemagic.cli import Colors
from codemagic.google import GoogleError
from codemagic.google.resources.google_play import Bundle
from codemagic.models.application_package import Aab
from codemagic.tools.google_play.action_groups.google_play_action_groups import GooglePlayActionGroups
from codemagic.tools.google_play.arguments import BundlesArgument
from codemagic.tools.google_play.errors import GooglePlayError
from codemagic.tools.google_play.google_play_base_action import GooglePlayBaseAction


class BundlesActionGroup(GooglePlayBaseAction, metaclass=ABCMeta):
    @cli.action(
        "list",
        action_group=GooglePlayActionGroups.BUNDLES,
    )
    def list_bundles(
        self,
        should_print: bool = True,
    ) -> List[Bundle]:
        """
        List APKs from Google Play for an app
        """

        try:
            with self.using_app_edit() as edit:
                bundles = self.client.bundles.list(self.package_name, edit.id)
        except GoogleError as ge:
            error_message = f'Listing APKS from Google Play for package "{self.package_name}" failed.'
            self.logger.warning(Colors.RED(error_message))
            raise GooglePlayError(str(ge))

        if not bundles:
            self.logger.warning(Colors.YELLOW(f'No App Bundles found for package "{self.package_name}"'))
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
        should_print: bool = True,
    ) -> Bundle:
        """
        Upload App Bundle at given path to Google Play
        """

        try:
            aab = Aab(bundle_path)
        except IOError:
            raise BundlesArgument.BUNDLE_PATH.raise_argument_error("Not a valid App Bundle file")

        self.logger.info(Colors.BLUE('Upload App Bundle "%s" to Google Play'), bundle_path)
        self.logger.info(aab.get_text_summary())

        try:
            with self.using_app_edit() as edit:
                bundle = self.client.bundles.upload(
                    self.package_name,
                    edit.id,
                    bundle_path=bundle_path,
                )
        except GoogleError as ge:
            error_message = f"Uploading App Bundle {bundle_path} to Google Play failed."
            self.logger.warning(Colors.RED(error_message))
            raise GooglePlayError(str(ge))

        self.printer.print_resource(bundle, should_print=should_print)
        return bundle
