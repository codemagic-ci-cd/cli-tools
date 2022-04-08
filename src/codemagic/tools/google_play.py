#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence

from codemagic import cli
from codemagic.google_play import GooglePlayDeveloperAPIClientError
from codemagic.google_play.api_client import GooglePlayDeveloperAPIClient
from codemagic.google_play.resources import Track


class Types:
    class PackageName(str):
        pass

    class CredentialsArgument(cli.EnvironmentArgumentValue[str]):
        environment_variable_key = 'GCLOUD_SERVICE_ACCOUNT_CREDENTIALS'

        @classmethod
        def _is_valid(cls, value: str) -> bool:
            try:
                json_content = json.loads(value)
            except json.decoder.JSONDecodeError:
                return False
            else:
                return json_content.get('type') == 'service_account'


class GooglePlayArgument(cli.Argument):
    GCLOUD_SERVICE_ACCOUNT_CREDENTIALS = cli.ArgumentProperties(
        key='credentials',
        flags=('--credentials',),
        type=Types.CredentialsArgument,
        description=(
            'Gcloud service account credentials with `JSON` key type '
            'to access Google Play Developer API'
        ),
        argparse_kwargs={'required': False},
    )
    JSON_OUTPUT = cli.ArgumentProperties(
        key='json_output',
        flags=('--json',),
        type=bool,
        description='Whether to show the request response in JSON format',
        argparse_kwargs={'required': False, 'action': 'store_true'},
    )


class TracksArgument(cli.Argument):
    PACKAGE_NAME = cli.ArgumentProperties(
        key='package_name',
        flags=('-p', '--package-name'),
        type=Types.PackageName,
        description='Package name of the app in Google Play Console (Ex: com.google.example)',
        argparse_kwargs={'required': True},
    )
    TRACK_NAME = cli.ArgumentProperties(
        key='track_name',
        flags=('-t', '--track'),
        description='Release track name. For example `alpha` or `production`',
        argparse_kwargs={'required': True},
    )


class BuildNumberArgument(cli.Argument):
    TRACKS = cli.ArgumentProperties(
        key='tracks',
        flags=('-t', '--tracks'),
        description=(
            'Get the build number from the specified track(s). '
            'If not specified, the highest build number across all tracks is returned'
        ),
        argparse_kwargs={
            'required': False,
            'nargs': '+',
        },
    )


class GooglePlayError(cli.CliAppException):
    pass


class GooglePlayActionGroups(cli.ActionGroup):
    TRACKS = cli.ActionGroupProperties(
        name='tracks',
        description='Manage your Google Play release tracks',
    )


@cli.common_arguments(GooglePlayArgument.GCLOUD_SERVICE_ACCOUNT_CREDENTIALS)
class GooglePlay(cli.CliApp):
    """
    Utility to get the latest build numbers from Google Play using Google Play Developer API
    """

    def __init__(
        self,
        credentials: str,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.credentials = credentials
        self.api_client = GooglePlayDeveloperAPIClient(credentials)

    @classmethod
    def from_cli_args(cls, cli_args: argparse.Namespace) -> GooglePlay:
        credentials_argument = GooglePlayArgument.GCLOUD_SERVICE_ACCOUNT_CREDENTIALS.from_args(cli_args)
        if credentials_argument is None:
            raise GooglePlayArgument.GCLOUD_SERVICE_ACCOUNT_CREDENTIALS.raise_argument_error()

        return GooglePlay(
            credentials=credentials_argument.value,
            **cls._parent_class_kwargs(cli_args),
        )

    @cli.action(
        'get-latest-build-number',
        TracksArgument.PACKAGE_NAME,
        BuildNumberArgument.TRACKS,
    )
    def get_latest_build_number(
        self,
        package_name: str,
        tracks: Optional[Sequence[str]] = None,
    ) -> Optional[int]:
        """
        Get latest build number from Google Play Developer API matching given constraints
        """

        package_tracks = self.list_tracks(package_name, should_print=False)
        track_version_codes: Dict[str, int] = {}

        for track in package_tracks:
            track_name = track.track
            if tracks and track_name not in tracks:
                continue
            try:
                version_code = track.get_max_version_code()
            except ValueError as ve:
                self.logger.warning(ve)
            else:
                self.logger.info(f'Latest version code for {track_name} track: {version_code}')
                track_version_codes[track_name] = version_code

        if not track_version_codes:
            raise GooglePlayError('Version code info is missing from all tracks')

        missing_track_names = set(tracks or []).difference(track_version_codes.keys())
        for missing_track_name in missing_track_names:
            self.logger.warning((
                f'Failed to get version code from Google Play for track "{missing_track_name}". '
                'Track was not found.'
            ))

        latest_build_number = max(track_version_codes.values())
        self.echo(str(latest_build_number))
        return latest_build_number

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


if __name__ == '__main__':
    GooglePlay.invoke_cli()
