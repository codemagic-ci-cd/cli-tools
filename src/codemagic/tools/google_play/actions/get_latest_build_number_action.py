from abc import ABCMeta
from itertools import chain
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence

from codemagic import cli
from codemagic.cli import Colors
from codemagic.google import GoogleError
from codemagic.google.resources.google_play import AppEdit
from codemagic.google.resources.google_play import Track
from codemagic.tools.google_play.arguments import GooglePlayArgument
from codemagic.tools.google_play.arguments import LatestBuildNumberArgument
from codemagic.tools.google_play.errors import GooglePlayError
from codemagic.tools.google_play.google_play_base_action import GooglePlayBaseAction


class GetLatestBuildNumberAction(GooglePlayBaseAction, metaclass=ABCMeta):
    @cli.action(
        "get-latest-build-number",
        GooglePlayArgument.PACKAGE_NAME,
        LatestBuildNumberArgument.TRACKS,
        LatestBuildNumberArgument.INCLUDE_UPLOADED_BUILDS,
    )
    def get_latest_build_number(
        self,
        package_name: str,
        tracks: Optional[Sequence[str]] = None,
        include_uploaded_builds: bool = False,
        should_print: bool = True,
    ) -> Optional[int]:
        """
        Get latest build number from Google Play matching given constraints
        """

        requested_track_names = tuple(tracks or [])
        if include_uploaded_builds and requested_track_names:
            raise GooglePlayError("Uploaded builds can only be included when no tracks are specified")

        self._log_get_package_action_started(package_name, requested_track_names, include_uploaded_builds)
        uploaded_version_code: Optional[int] = None
        try:
            with self.using_app_edit(package_name) as edit:
                package_tracks = self.list_tracks(package_name, edit=edit, should_print=False)
                if include_uploaded_builds:
                    uploaded_version_code = self._get_max_uploaded_version_code(package_name, edit)
        except GoogleError as ge:
            raise GooglePlayError(str(ge))

        track_version_codes = self._get_max_track_version_codes(requested_track_names, package_tracks)
        self._show_missing_tracks_warnings(requested_track_names, tuple(track_version_codes.keys()))
        latest_build_number = self._get_latest_build_number(
            package_name,
            requested_track_names,
            track_version_codes,
            uploaded_version_code,
            include_uploaded_builds,
        )

        if should_print:
            self.echo(str(latest_build_number))

        return latest_build_number

    def _log_get_package_action_started(
        self,
        package_name: str,
        requested_tracks: Sequence[str],
        include_uploaded_builds: bool = False,
    ):
        if include_uploaded_builds:
            message = f'Get package "{package_name}" latest build number across all tracks and uploaded builds'
        elif not requested_tracks:
            message = f'Get package "{package_name}" latest build number across all tracks'
        elif len(requested_tracks) == 1:
            message = f'Get package "{package_name}" latest build number from track "{requested_tracks[0]}"'
        else:
            formatted_specified_tracks = ", ".join(f'"{track}"' for track in requested_tracks)
            message = f'Get package "{package_name}" latest build number from tracks {formatted_specified_tracks}'
        self.logger.info(Colors.BLUE(message))

    def _get_max_track_version_codes(
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
                max_version_code = self.get_max_version_code(track)
            except ValueError as ve:
                self.logger.warning(ve)
                track_version_codes[track_name] = None
            else:
                self.logger.info(f'Found latest version code from "{track_name}" track: {max_version_code}')
                track_version_codes[track_name] = max_version_code

        return track_version_codes

    @classmethod
    def get_max_version_code(cls, track: Track) -> int:
        error_prefix = f'Failed to get version code from "{track.track}" track'
        if not track.releases:
            raise ValueError(f"{error_prefix}: track has no releases")
        version_codes = [release.versionCodes for release in track.releases if release.versionCodes]
        if not version_codes:
            raise ValueError(f"{error_prefix}: releases with version code do not exist")
        return max(map(int, chain(*version_codes)))

    def _get_max_uploaded_version_code(self, package_name: str, edit: AppEdit) -> Optional[int]:
        try:
            bundles = self.client.bundles.list(package_name, edit.id)
            apks = self.client.apks.list(package_name, edit.id)
        except GoogleError as ge:
            error_message = f'Listing uploaded builds from Google Play for package "{package_name}" failed.'
            self.logger.warning(Colors.RED(error_message))
            raise GooglePlayError(str(ge))

        version_codes: List[int] = [int(bundle.versionCode) for bundle in bundles]
        version_codes.extend(int(apk.versionCode) for apk in apks)
        if not version_codes:
            self.logger.warning(Colors.YELLOW(f'No uploaded App Bundles or APKs found for package "{package_name}"'))
            return None

        max_version_code = max(version_codes)
        self.logger.info(f"Found latest version code from uploaded App Bundles and APKs: {max_version_code}")
        return max_version_code

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
        uploaded_version_code: Optional[int] = None,
        include_uploaded_builds: bool = False,
    ) -> int:
        version_codes = [version_code for version_code in track_version_codes.values() if version_code is not None]
        if uploaded_version_code is not None:
            version_codes.append(uploaded_version_code)
        if not version_codes:
            error = self._get_missing_version_error(package_name, requested_tracks, include_uploaded_builds)
            raise GooglePlayError(error)
        return max(version_codes)

    @classmethod
    def _get_missing_version_error(
        cls,
        package_name: str,
        requested_tracks: Sequence[str],
        include_uploaded_builds: bool = False,
    ) -> str:
        if include_uploaded_builds:
            return f'Version code info is missing from all tracks and uploaded builds for package "{package_name}"'
        elif not requested_tracks:
            return f'Version code info is missing from all tracks for package "{package_name}"'
        elif len(requested_tracks) == 1:
            _track = requested_tracks[0]
            return f'Version code info is missing from track "{_track}" for package "{package_name}"'
        else:
            _tracks = ", ".join(f'"{track}"' for track in requested_tracks)
            return f'Version code info is missing from tracks {_tracks} for package "{package_name}"'
