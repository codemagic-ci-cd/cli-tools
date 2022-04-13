from abc import ABCMeta
from typing import Dict
from typing import Optional
from typing import Sequence

from codemagic import cli
from codemagic.cli import Colors
from codemagic.google_play.resources import Track

from ..arguments import LatestBuildNumberArgument
from ..arguments import TracksArgument
from ..errors import GooglePlayError
from ..google_play_base_action import GooglePlayBaseAction


class GetLatestBuildNumberAction(GooglePlayBaseAction, metaclass=ABCMeta):
    @cli.action(
        'get-latest-build-number',
        TracksArgument.PACKAGE_NAME,
        LatestBuildNumberArgument.TRACKS,
    )
    def get_latest_build_number(
        self,
        package_name: str,
        tracks: Optional[Sequence[str]] = None,
    ) -> Optional[int]:
        """
        Get latest build number from Google Play Developer API matching given constraints
        """

        requested_track_names = tuple(tracks or [])
        self._log_get_package_action_started(package_name, requested_track_names)
        package_tracks = self.list_tracks(package_name, should_print=False)
        track_version_codes = self._get_track_version_codes(requested_track_names, package_tracks)
        self._show_missing_tracks_warnings(requested_track_names, tuple(track_version_codes.keys()))
        latest_build_number = self._get_latest_build_number(package_name, requested_track_names, track_version_codes)

        self.echo(str(latest_build_number))
        return latest_build_number

    def _log_get_package_action_started(self, package_name: str, requested_tracks: Sequence[str]):
        if not requested_tracks:
            message = f'Get package "{package_name}" latest build number across all tracks'
        elif len(requested_tracks) == 1:
            message = f'Get package "{package_name}" latest build number from track "{requested_tracks[0]}"'
        else:
            formatted_specified_tracks = ', '.join(f'"{track}"' for track in requested_tracks)
            message = f'Get package "{package_name}" latest build number from tracks {formatted_specified_tracks}'
        self.logger.info(Colors.BLUE(message))

    def _get_track_version_codes(
        self,
        requested_tracks: Sequence[str],
        package_tracks: Sequence[Track],
    ) -> Dict[str, Optional[int]]:
        track_version_codes: Dict[str, Optional[int]] = {}

        for track in package_tracks:
            track_name = track.track
            if requested_tracks and track_name not in requested_tracks:
                continue

            try:
                version_code = track.get_max_version_code()
            except ValueError as ve:
                self.logger.warning(ve)
                track_version_codes[track_name] = None
            else:
                self.logger.info(f'Found latest version code from "{track_name}" track: {version_code}')
                track_version_codes[track_name] = version_code

        return track_version_codes

    def _show_missing_tracks_warnings(self, requested_tracks: Sequence[str], found_tracks: Sequence[str]):
        missing_track_names = set(requested_tracks).difference(found_tracks)
        for missing_track_name in missing_track_names:
            message = f'Failed to get version code from track "{missing_track_name}": track was not found'
            self.logger.warning(Colors.YELLOW(message))

    def _get_latest_build_number(
        self,
        package_name: str,
        requested_tracks: Sequence[str],
        track_version_codes: Dict[str, Optional[int]],
    ) -> int:
        version_codes = [version_code for version_code in track_version_codes.values() if version_code is not None]
        if not version_codes:
            error = self._get_missing_version_error(package_name, requested_tracks)
            raise GooglePlayError(error)
        return max(version_codes)

    @classmethod
    def _get_missing_version_error(cls, package_name: str, requested_tracks: Sequence[str]) -> str:
        if not requested_tracks:
            return f'Version code info is missing from all tracks for package "{package_name}'
        elif len(requested_tracks) == 1:
            _track = requested_tracks[0]
            return f'Version code info is missing from track "{_track}" for package "{package_name}'
        else:
            _tracks = ', '.join(f'"{track}"' for track in requested_tracks)
            return f'Version code info is missing from tracks {_tracks} for package "{package_name}'
