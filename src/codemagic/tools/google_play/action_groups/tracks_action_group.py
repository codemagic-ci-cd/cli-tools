import dataclasses
import json
from abc import ABCMeta
from typing import List
from typing import Optional

from codemagic import cli
from codemagic.cli import Colors
from codemagic.google_play import GooglePlayDeveloperAPIClientError
from codemagic.google_play.resources import Release
from codemagic.google_play.resources import ReleaseStatus
from codemagic.google_play.resources import Track

from ..arguments import GooglePlayArgument
from ..arguments import PromoteArgument
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
        "promote-release",
        TracksArgument.PACKAGE_NAME,
        PromoteArgument.SOURCE_TRACK_NAME,
        PromoteArgument.TARGET_TRACK_NAME,
        PromoteArgument.PROMOTED_STATUS,
        PromoteArgument.PROMOTED_USER_FRACTION,
        PromoteArgument.PROMOTE_VERSION_CODE,
        PromoteArgument.PROMOTE_STATUS,
        GooglePlayArgument.JSON_OUTPUT,
        action_group=GooglePlayActionGroups.TRACKS,
    )
    def promote_release(
        self,
        package_name: str,
        source_track_name: str,
        target_track_name: str,
        promoted_status: ReleaseStatus = PromoteArgument.PROMOTED_STATUS.get_default(),
        promoted_user_fraction: Optional[float] = None,
        promote_version_code: Optional[str] = None,
        promote_status: Optional[ReleaseStatus] = None,
        json_output: bool = False,
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
            error = f'Source track "{source_track_name}" does not have any releases'
            if promote_version_code or promote_status:
                error = f"{error} matching specified filters"
            raise GooglePlayError(error)

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

        try:
            updated_track = self.api_client.update_track(
                package_name,
                dataclasses.replace(target_track, releases=[release_to_promote]),
            )
        except GooglePlayDeveloperAPIClientError as api_error:
            raise GooglePlayError(str(api_error))

        self.logger.info(Colors.GREEN(f"Successfully completed release promotion to track {target_track.track}"))

        if should_print:
            self.echo(updated_track.json() if json_output else str(updated_track))

        return updated_track
