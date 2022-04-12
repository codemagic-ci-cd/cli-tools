#!/usr/bin/env python3

from __future__ import annotations

import argparse
from typing import Union

from codemagic import cli
from codemagic.google_play.api_client import GooglePlayDeveloperAPIClient

from .action_groups import TracksActionGroup
from .actions import GetLatestBuildNumberAction
from .arguments import GooglePlayArgument


@cli.common_arguments(GooglePlayArgument.GCLOUD_SERVICE_ACCOUNT_CREDENTIALS)
class GooglePlay(
    cli.CliApp,
    GetLatestBuildNumberAction,
    TracksActionGroup,
):
    """
    Utility to get the latest build numbers from Google Play using Google Play Developer API
    """

    def __init__(self, credentials: Union[str, dict], **kwargs):
        super().__init__(**kwargs)
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


if __name__ == '__main__':
    GooglePlay.invoke_cli()
