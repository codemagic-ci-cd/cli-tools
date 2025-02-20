#!/usr/bin/env python3

from __future__ import annotations

import argparse
import contextlib
from typing import Generator
from typing import Optional
from typing import cast

from codemagic import cli
from codemagic.google import GooglePlayClient
from codemagic.google.resources import ResourcePrinter
from codemagic.google.resources.google_play import AppEdit

from .action_groups import TracksActionGroup
from .actions import GetLatestBuildNumberAction
from .arguments import GooglePlayArgument


@cli.common_arguments(
    GooglePlayArgument.GOOGLE_PLAY_SERVICE_ACCOUNT_CREDENTIALS,
    GooglePlayArgument.JSON_OUTPUT,
)
class GooglePlay(
    cli.CliApp,
    GetLatestBuildNumberAction,
    TracksActionGroup,
):
    """
    Utility to get the latest build numbers from Google Play using Google Play Developer API
    """

    def __init__(
        self,
        credentials: dict,
        json_output: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.client = GooglePlayClient(credentials)
        self.printer = ResourcePrinter(json_output, self.echo)

    @classmethod
    def from_cli_args(cls, cli_args: argparse.Namespace) -> GooglePlay:
        credentials_argument = GooglePlayArgument.GOOGLE_PLAY_SERVICE_ACCOUNT_CREDENTIALS.from_args(cli_args)
        if credentials_argument is None:
            raise GooglePlayArgument.GOOGLE_PLAY_SERVICE_ACCOUNT_CREDENTIALS.raise_argument_error()

        return GooglePlay(
            credentials=credentials_argument.value,
            json_output=bool(cli_args.json_output),
            **cls._parent_class_kwargs(cli_args),
        )

    @contextlib.contextmanager
    def using_app_edit(self, package_name: str) -> Generator[AppEdit, None, None]:
        edit: Optional[AppEdit] = None
        try:
            edit = self.client.edits.create(package_name=package_name)
            yield cast(AppEdit, edit)
        finally:
            if edit is not None:
                self.client.edits.delete(edit, package_name=package_name)


if __name__ == "__main__":
    GooglePlay.invoke_cli()
