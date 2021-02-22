#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from typing import Optional
from typing import Sequence

from codemagic import cli
from codemagic.google_play import GooglePlayDeveloperAPIClient
from codemagic.google_play import GooglePlayDeveloperAPIClientError
from codemagic.google_play.enums import Track
from codemagic.google_play.types import Credentials
from codemagic.google_play.types import CredentialsArgument
from codemagic.google_play.types import PackageName


class GooglePlayArgument(cli.Argument):
    GCLOUD_SERVICE_ACCOUNT_CREDENTIALS = cli.ArgumentProperties(
        key='credentials',
        flags=('--credentials',),
        type=CredentialsArgument,
        description=(
            'Gcloud service account creedentials with `JSON` key type '
            'to access Google Play Developer API'
        ),
        argparse_kwargs={'required': False}
    )
    PACKAGE_NAME = cli.ArgumentProperties(
        key='package_name',
        flags=('--package-name',),
        type=PackageName,
        description='Package name of the app in Google Play Console (Ex: com.google.example)',
        argparse_kwargs={'required': True}
    )


class BuildNumberArgument(cli.Argument):
    TRACK = cli.ArgumentProperties(
        key='track',
        flags=('--track',),
        type=Track,
        description=(
            'Get the build number from the specified track. '
            'If not specified, the maximum number across all tracks is returned'
        ),
        argparse_kwargs={
            'required': False,
            'nargs': '+',
            'choices': list(Track),
        }
    )


class GooglePlayError(cli.CliAppException):
    pass


@cli.common_arguments(*GooglePlayArgument)
class GooglePlay(cli.CliApp):
    """
    Utility to get the latest build numbers from Google Play using Google Play Developer API
    """

    def  __init__(self,
                  credentials: Credentials,
                  package_name: PackageName,
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
            credentials=credentials_argument.value,
            package_name=package_name_argument.value,
            **cls._parent_class_kwargs(cli_args)
        )

    @cli.action('get-latest-build-number', BuildNumberArgument.TRACK)
    def get_latest_build_number(self, track: Sequence[Track] = None) -> Optional[int]:
        """
        Get latest build number from Google Play Developer API matching given constraints
        """
        try:
            edit = self.api_client.create_edit()
            return 0
        except GooglePlayDeveloperAPIClientError as api_error:
            raise GooglePlayError(str(api_error))



if __name__ == '__main__':
    GooglePlay.invoke_cli()