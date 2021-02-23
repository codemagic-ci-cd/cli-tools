#!/usr/bin/env python3

from __future__ import annotations

import argparse
from itertools import chain
from typing import Optional
from typing import Sequence

from codemagic import cli
from codemagic.google_play import GooglePlayDeveloperAPIClientError
from codemagic.google_play import GooglePlayTypes
from codemagic.google_play import Track
from codemagic.google_play import VersionCodeFromTrackError
from codemagic.google_play.api_client import GooglePlayDeveloperAPIClient


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


class BuildNumberArgument(cli.Argument):
    TRACKS = cli.ArgumentProperties(
        key='tracks',
        flags=('--tracks',),
        type=Track,
        description=(
            'Get the build number from the specified track(s). '
            'If not specified, the highest build number across all tracks is returned'
        ),
        argparse_kwargs={
            'required': False,
            'nargs': '+',
            'choices': list(Track),
            'default': ' '.join(list(map(str, Track))),
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
                 credentials: GooglePlayTypes.Credentials,
                 package_name: GooglePlayTypes.PackageName,
                 **kwargs):
        super().__init__(**kwargs)
        self.credentials = credentials
        self.package_name = package_name
        self.api_client = GooglePlayDeveloperAPIClient(credentials, package_name)

    @classmethod
    def from_cli_args(cls, cli_args: argparse.Namespace) -> GooglePlay:
        credentials_argument = GooglePlayArgument.GCLOUD_SERVICE_ACCOUNT_CREDENTIALS.from_args(cli_args)
        package_name_argument = GooglePlayArgument.PACKAGE_NAME.from_args(cli_args)

        if credentials_argument is None:
            raise GooglePlayArgument.GCLOUD_SERVICE_ACCOUNT_CREDENTIALS.raise_argument_error()
        if package_name_argument is None:
            raise GooglePlayArgument.PACKAGE_NAME.raise_argument_error()

        return GooglePlay(
            credentials=credentials_argument,
            package_name=package_name_argument,
            **cls._parent_class_kwargs(cli_args),
        )

    @cli.action('get-latest-build-number', BuildNumberArgument.TRACKS)
    def get_latest_build_number(self, tracks: Sequence[Track] = None) -> Optional[int]:
        """
        Get latest build number from Google Play Developer API matching given constraints
        """

        try:
            edit = self.api_client.create_edit()
        except GooglePlayDeveloperAPIClientError as api_error:
            raise GooglePlayError(str(api_error))

        track_version_codes = []
        if not tracks:
            tracks = list(Track)
        for track in tracks:
            try:
                track_response = self.api_client.get_track_information(edit['id'], track)
                releases = track_response.get('releases', [])
                if not releases:
                    raise VersionCodeFromTrackError(self.package_name, track.value, 'No release information')
                version_codes = [release['versionCodes'] for release in releases if release.get('versionCodes')]
                if not version_codes:
                    raise VersionCodeFromTrackError(
                        self.package_name, track.value, 'No releases with uploaded App bundles or APKs')
                version_code = max(map(int, chain(*version_codes)))
            except GooglePlayDeveloperAPIClientError as api_error:
                self.logger.warning(api_error)
            else:
                self.logger.info(f'Latest version code for {track.value} track: {version_code}')
                track_version_codes.append(version_code)
        try:
            self.api_client.delete_edit(edit['id'])
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
