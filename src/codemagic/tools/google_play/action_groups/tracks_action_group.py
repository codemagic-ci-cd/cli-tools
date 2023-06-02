import json
from abc import ABCMeta
from typing import List

from codemagic import cli
from codemagic.google_play import GooglePlayDeveloperAPIClientError
from codemagic.google_play.resources import Track

from ..arguments import GooglePlayArgument
from ..arguments import TracksArgument
from ..errors import GooglePlayError
from ..google_play_base_action import GooglePlayBaseAction
from .google_play_action_groups import GooglePlayActionGroups


class TracksActionGroup(GooglePlayBaseAction, metaclass=ABCMeta):
    @cli.action(
        'get',
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
        'list',
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
                    self.echo(str(track))

        return tracks
