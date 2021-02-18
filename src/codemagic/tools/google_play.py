#!/usr/bin/env python3

from __future__ import annotations

import argparse
import enum
import json
from typing import Optional

from codemagic import cli
from codemagic.google_play import GooglePlayDeveloperAPIClient
from codemagic.google_play import GooglePlayDeveloperAPIClientError


class Types:
    class ServiceAccountCredentials(cli.EnvironmentArgumentValue[str]):
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
        type=Types.ServiceAccountCredentials,
        description=(
            'Gcloud service account creedentials with `JSON` key type '
            'to access Google Play Developer API'
        ),
        argparse_kwargs={'required': True}
    )
    PACKAGE_NAME = cli.ArgumentProperties(
        key='package_name',
        type=str,
        description='Package name of the app in Google Play Console (Ex: com.google.example)',
        argparse_kwargs={'required': True}
    )


class BuildNumberArgument(cli.Argument):
    TRACK = cli.ArgumentProperties(
        key='track',
        type=Track,
        description=(
            'Get the build number from the specified track. '
            'If not specified, the maximum number across all tracks is returned'
        ),
        argparse_kwargs={
            'required': False,
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
                  credentials: Types.ServiceAccountCredentials,
                  package_name: str,
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
def get_latest_build_number(self, track: Optional[Track] = None) -> Optional[int]:
    try:
        edit = self.api_client.create_edit()
    except GooglePlayDeveloperAPIClientError as api_error:
        raise GooglePlayError(str(api_error))



if __name__ == '__main__':
    GooglePlay.invoke_cli()