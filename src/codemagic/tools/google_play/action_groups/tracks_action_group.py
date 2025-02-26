import dataclasses
from abc import ABCMeta
from typing import List
from typing import Optional

from codemagic import cli
from codemagic.cli import Colors
from codemagic.google import GoogleError
from codemagic.google.resources.google_play import AppEdit
from codemagic.google.resources.google_play import Release
from codemagic.google.resources.google_play import Status
from codemagic.google.resources.google_play import Track
from codemagic.tools.google_play.arguments import GooglePlayArgument
from codemagic.tools.google_play.arguments import PromoteArgument
from codemagic.tools.google_play.arguments import TracksArgument
from codemagic.tools.google_play.errors import GooglePlayError
from codemagic.tools.google_play.google_play_base_action import GooglePlayBaseAction

from .google_play_action_groups import GooglePlayActionGroups


class TracksActionGroup(GooglePlayBaseAction, metaclass=ABCMeta):
    @cli.action(
        "get",
        GooglePlayArgument.PACKAGE_NAME,
        TracksArgument.TRACK_NAME,
        action_group=GooglePlayActionGroups.TRACKS,
    )
    def get_track(
        self,
        package_name: str,
        track_name: str,
        edit: Optional[AppEdit] = None,
        should_print: bool = True,
    ) -> Track:
        """
        Get information about release track from Google Play for an app
        """

        try:
            with self.using_app_edit(package_name, edit) as edit:
                track = self.client.tracks.get(package_name, track_name, edit.id)
        except GoogleError as ge:
            error_message = f'Getting track "{track_name}" from Google Play for package "{package_name}" failed.'
            self.logger.warning(Colors.RED(error_message))
            raise GooglePlayError(str(ge))

        self.printer.print_resource(track, should_print)
        return track

    @cli.action(
        "list",
        GooglePlayArgument.PACKAGE_NAME,
        action_group=GooglePlayActionGroups.TRACKS,
    )
    def list_tracks(
        self,
        package_name: str,
        edit: Optional[AppEdit] = None,
        should_print: bool = True,
    ) -> List[Track]:
        """
        List information about release tracks from Google Play for an app
        """

        try:
            with self.using_app_edit(package_name, edit) as edit:
                tracks = self.client.tracks.list(package_name, edit.id)
        except GoogleError as ge:
            error_message = f'Listing tracks from Google Play for package "{package_name}" failed.'
            self.logger.warning(Colors.RED(error_message))
            raise GooglePlayError(str(ge))

        self.printer.print_resources(tracks, should_print)
        return tracks

    @cli.action(
        "promote-release",
        GooglePlayArgument.PACKAGE_NAME,
        PromoteArgument.SOURCE_TRACK_NAME,
        PromoteArgument.TARGET_TRACK_NAME,
        PromoteArgument.PROMOTED_STATUS,
        PromoteArgument.PROMOTED_USER_FRACTION,
        PromoteArgument.PROMOTE_VERSION_CODE,
        PromoteArgument.PROMOTE_STATUS,
        action_group=GooglePlayActionGroups.TRACKS,
    )
    def promote_release(
        self,
        package_name: str,
        source_track_name: str,
        target_track_name: str,
        promoted_status: Status = PromoteArgument.PROMOTED_STATUS.get_default(),
        promoted_user_fraction: Optional[float] = None,
        promote_version_code: Optional[str] = None,
        promote_status: Optional[Status] = None,
        should_print: bool = True,
    ) -> Track:
        """
        Promote releases from source track to target track. If filters for source
        track release are not specified, then the latest release will be promoted
        """

        source_track = self.get_track(package_name, source_track_name, should_print=False)
        target_track = self.get_track(package_name, target_track_name, should_print=False)

        source_releases: List[Release] = source_track.releases or []
        if promote_version_code:
            source_releases = [r for r in source_releases if r.versionCodes and promote_version_code in r.versionCodes]
        if promote_status:
            source_releases = [r for r in source_releases if r.status is promote_status]

        if not source_releases:
            error_message = f'Source track "{source_track_name}" does not have any releases'
            if promote_version_code or promote_status:
                error_message = f"{error_message} matching specified filters"
            raise GooglePlayError(error_message)

        release_to_promote = dataclasses.replace(
            source_releases[0],
            status=promoted_status,
            userFraction=promoted_user_fraction,
        )

        promoted_version_codes = ", ".join(release_to_promote.versionCodes or ["version code N/A"])
        self.logger.info(
            f"Promote release {release_to_promote.name} ({promoted_version_codes}) "
            f'from track "{source_track.track}" to track "{target_track.track}"',
        )

        update_track = dataclasses.replace(target_track, releases=[release_to_promote])
        try:
            edit = self.client.edits.create(package_name)
            updated_track = self.client.tracks.update(update_track, package_name, edit.id)
            self.client.edits.commit(edit, package_name)
        except GoogleError as ge:
            error_message = (
                f"Promoting release {release_to_promote.name} from "
                f'track "{source_track.track}" to track "{target_track.track}" failed.'
            )
            self.logger.warning(Colors.RED(error_message))
            raise GooglePlayError(str(ge))

        self.logger.info(Colors.GREEN(f"Successfully completed release promotion to track {target_track.track}"))
        self.printer.print_resource(updated_track, should_print)
        return updated_track
