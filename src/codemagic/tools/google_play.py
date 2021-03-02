#!/usr/bin/env python3

from __future__ import annotations

import argparse
from typing import List
from typing import Optional
from typing import Sequence

from codemagic import cli
from codemagic.google_play import GooglePlayDeveloperAPIClientError
from codemagic.google_play import GooglePlayTypes
from codemagic.google_play.api_client import GooglePlayDeveloperAPIClient
from codemagic.google_play.api_client import ResourcePrinter
from codemagic.google_play.resources import Edit
from codemagic.google_play.resources import Track
from codemagic.google_play.resources import TrackName


class GooglePlayArgument(cli.Argument):
    GCLOUD_SERVICE_ACCOUNT_CREDENTIALS = cli.ArgumentProperties(
        key='credentials',
        flags=('--credentials',),
        type=GooglePlayTypes.CredentialsArgument,
        description=(
            'Gcloud service account creedentials with `JSON` key type '
            'to access Google Play Developer API'
        ),
        argparse_kwargs={'required': False},
    )
    PACKAGE_NAME = cli.ArgumentProperties(
        key='package_name',
        flags=('--package-name',),
        type=GooglePlayTypes.PackageName,
        description='Package name of the app in Google Play Console (Ex: com.google.example)',
        argparse_kwargs={'required': True},
    )
    LOG_REQUESTS = cli.ArgumentProperties(
        key='log_requests',
        flags=('--log-api-calls',),
        type=bool,
        description='Turn on logging for Google Play Developer API requests',
        argparse_kwargs={'required': False, 'action': 'store_true'},
    )
    JSON_OUTPUT = cli.ArgumentProperties(
        key='json_output',
        flags=('--json',),
        type=bool,
        description='Whether to show the request response in JSON format',
        argparse_kwargs={'required': False, 'action': 'store_true'},
    )


class BuildNumberArgument(cli.Argument):
    TRACKS = cli.ArgumentProperties(
        key='tracks',
        flags=('--tracks',),
        type=TrackName,
        description=(
            'Get the build number from the specified track(s). '
            f'If not specified, the highest build number across all tracks ({", ".join(list(map(str, TrackName)))}) is returned'
        ),
        argparse_kwargs={
            'required': False,
            'nargs': '+',
            'choices': list(TrackName),
        },
    )


class GooglePlayError(cli.CliAppException):
    pass


@cli.common_arguments(*GooglePlayArgument)
class GooglePlay(cli.CliApp):
    """
    Utility to get the latest build numbers from Google Play using Google Play Developer API
    """

    def __init__(self,
                 credentials: str,
                 package_name: GooglePlayTypes.PackageName,
                 log_requests: bool = False,
                 json_output: bool = False,
                 **kwargs):
        super().__init__(**kwargs)
        self.credentials = credentials
        self.package_name = package_name
        print_command = self.echo if kwargs['enable_logging'] else None
        printer = ResourcePrinter(bool(log_requests), bool(json_output), print_command)
        self.api_client = GooglePlayDeveloperAPIClient(credentials, package_name, printer)

    @classmethod
    def from_cli_args(cls, cli_args: argparse.Namespace) -> GooglePlay:
        credentials_argument = GooglePlayArgument.GCLOUD_SERVICE_ACCOUNT_CREDENTIALS.from_args(cli_args)
        package_name_argument = GooglePlayArgument.PACKAGE_NAME.from_args(cli_args)

        if credentials_argument is None:
            raise GooglePlayArgument.GCLOUD_SERVICE_ACCOUNT_CREDENTIALS.raise_argument_error()
        if package_name_argument is None:
            raise GooglePlayArgument.PACKAGE_NAME.raise_argument_error()

        return GooglePlay(
            credentials=credentials_argument.value,
            package_name=package_name_argument,
            log_requests=cli_args.log_requests,
            json_output=cli_args.json_output,
            **cls._parent_class_kwargs(cli_args),
        )

    @cli.action('get-latest-build-number', BuildNumberArgument.TRACKS)
    def get_latest_build_number(self, tracks: Sequence[TrackName] = None) -> Optional[int]:
        """
        Get latest build number from Google Play Developer API matching given constraints
        """

        try:
            edit: Edit = self.api_client.create_edit()
        except GooglePlayDeveloperAPIClientError as api_error:
            raise GooglePlayError(str(api_error))

        track_version_codes: List[int] = []
        track_names: Sequence[TrackName] = tracks or list(TrackName)
        for track_name in track_names:
            try:
                track: Track = self.api_client.get_track_information(edit.id, track_name)
                version_code: int = track.max_version_code
            except GooglePlayDeveloperAPIClientError as api_error:
                self.logger.warning(api_error)
            else:
                self.logger.info(f'Latest version code for {track_name.value} track: {str(version_code)}')
                track_version_codes.append(version_code)
        try:
            self.api_client.delete_edit(edit.id)
        except GooglePlayDeveloperAPIClientError as api_error:
            self.logger.warning(api_error)

        try:
            latest_build_number = max(track_version_codes)
        except ValueError:
            raise GooglePlayError('Version code info is missing from all tracks')
        self.echo(str(latest_build_number))
        return latest_build_number


if __name__ == '__main__':
    GooglePlay.invoke_cli()
