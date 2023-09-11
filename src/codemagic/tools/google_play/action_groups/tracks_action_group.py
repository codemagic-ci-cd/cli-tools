import dataclasses
import json
from abc import ABCMeta
from typing import List

from codemagic import cli
from codemagic.cli import Colors
from codemagic.google_play import GooglePlayDeveloperAPIClientError
from codemagic.google_play.resources import ReleaseStatus
from codemagic.google_play.resources import Track

from ..arguments import GooglePlayArgument
from ..arguments import TracksArgument
from ..errors import GooglePlayError
from ..google_play_base_action import GooglePlayBaseAction
from .google_play_action_groups import GooglePlayActionGroups


class TracksActionGroup(GooglePlayBaseAction, metaclass=ABCMeta):
    @cli.action(
        "get",
        TracksArgument.PACKAGE_NAME,
        TracksArgument.TRACK_NAME,
        GooglePlayArgument.JSON_OUTPUT,
        action_group=GooglePlayActionGroups.TRACKS,
    )
    def get_track(
        self,
        package_name: str,
        track_name: str,
        json_output: bool = False,
        should_print: bool = True,
    ) -> Track:
        """
        Get information about specified track from Google Play Developer API
        """

        try:
            track = self.api_client.get_track(package_name, track_name)
        except GooglePlayDeveloperAPIClientError as api_error:
            raise GooglePlayError(str(api_error))

        if should_print:
            self.logger.info(track.json() if json_output else str(track))

        return track

    @cli.action(
        "list",
        TracksArgument.PACKAGE_NAME,
        GooglePlayArgument.JSON_OUTPUT,
        action_group=GooglePlayActionGroups.TRACKS,
    )
    def list_tracks(
        self,
        package_name: str,
        json_output: bool = False,
        should_print: bool = True,
    ) -> List[Track]:
        """
        Get information about specified track from Google Play Developer API
        """

        try:
            tracks = self.api_client.list_tracks(package_name)
        except GooglePlayDeveloperAPIClientError as api_error:
            raise GooglePlayError(str(api_error))

        if should_print:
            if json_output:
                self.echo(json.dumps([t.dict() for t in tracks], indent=4))
            else:
                for track in tracks:
                    self.echo(f"{track}\n")

        return tracks

    @cli.action(
        "promote",
        TracksArgument.PACKAGE_NAME,
        TracksArgument.SOURCE_TRACK_NAME,
        TracksArgument.TARGET_TRACK_NAME,
        TracksArgument.TRACK_PROMOTED_RELEASE_STATUS,
        GooglePlayArgument.JSON_OUTPUT,
        action_group=GooglePlayActionGroups.TRACKS,
    )
    def promote_track(
        self,
        package_name: str,
        source_track_name: str,
        target_track_name: str,
        promoted_release_status: ReleaseStatus = TracksArgument.TRACK_PROMOTED_RELEASE_STATUS.get_default(),
        json_output: bool = False,
        should_print: bool = True,
    ) -> Track:
        """
        Promote releases from source track to target track
        """

        source_track = self.get_track(package_name, source_track_name, should_print=False)
        target_track = self.get_track(package_name, target_track_name, should_print=False)

        if not source_track.releases:
            raise GooglePlayError("Source track does not have any releases")

        release_to_promote = dataclasses.replace(
            source_track.releases[0],
            status=promoted_release_status,
        )

        promoted_version_codes = ", ".join(release_to_promote.versionCodes or ["version code N/A"])
        self.logger.info(
            f"Promote release {release_to_promote.name} ({promoted_version_codes}) "
            f'from track "{source_track.track}" to track "{target_track.track}"',
        )

        try:
            updated_track = self.api_client.update_track(
                package_name,
                dataclasses.replace(target_track, releases=[release_to_promote]),
            )
        except GooglePlayDeveloperAPIClientError as api_error:
            raise GooglePlayError(str(api_error))

        self.logger.info(Colors.GREEN(f"Successfully Completed release promotion to track {target_track.track}"))

        if should_print:
            self.echo(updated_track.json() if json_output else str(updated_track))

        return updated_track
