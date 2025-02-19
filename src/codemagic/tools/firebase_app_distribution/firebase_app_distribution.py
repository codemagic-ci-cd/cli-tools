#!/usr/bin/env python3

from __future__ import annotations

import argparse
from typing import Dict
from typing import Optional

from codemagic import cli
from codemagic.google.firebase_client import FirebaseClient
from codemagic.google.resources import ResourcePrinter
from codemagic.utilities import log
from codemagic.utilities.decorators import deprecated

from .action_groups import ReleasesActionGroup
from .actions import GetLatestBuildVersionAction
from .arguments import FirebaseArgument


@cli.common_arguments(
    FirebaseArgument.PROJECT_ID,
    FirebaseArgument.PROJECT_NUMBER,
    FirebaseArgument.FIREBASE_SERVICE_ACCOUNT_CREDENTIALS,
    FirebaseArgument.JSON_OUTPUT,
)
class FirebaseAppDistribution(
    cli.CliApp,
    GetLatestBuildVersionAction,
    ReleasesActionGroup,
):
    """
    Utility to list releases and retrieve the latest release build version number from Firebase
    """

    def __init__(
        self,
        credentials: Dict,
        project_number: Optional[str] = None,
        project_id: Optional[str] = None,
        json_output: bool = False,
        **kwargs,
    ):
        if not project_id and not project_number:
            raise ValueError("Missing project_number")
        super().__init__(**kwargs)
        self.client = FirebaseClient(credentials)
        self._project_id = project_id
        self._project_number = project_number
        self.printer = ResourcePrinter(json_output, self.echo)
        if project_id:
            _ = self.project_id  # Just to trigger deprecation warning

    @property
    @deprecated("0.53.5", 'Use "FirebaseAppDistribution.project_number" instead.')
    def project_id(self):
        return self.project_number

    @property
    def project_number(self):
        if not self._project_number:
            return self._project_id
        return self._project_number

    @classmethod
    def from_cli_args(cls, cli_args: argparse.Namespace) -> FirebaseAppDistribution:
        credentials_argument = FirebaseArgument.FIREBASE_SERVICE_ACCOUNT_CREDENTIALS.from_args(cli_args)
        if credentials_argument is None:
            raise FirebaseArgument.FIREBASE_SERVICE_ACCOUNT_CREDENTIALS.raise_argument_error()
        project_id = FirebaseArgument.PROJECT_ID.from_args(cli_args)
        if project_id:
            message = (
                "Deprecation warning! "
                f'Flag "{FirebaseArgument.get_flag(FirebaseArgument.PROJECT_ID)}" was deprecated in version 0.53.5 '
                "and is subject for removal in future releases. "
                f'Use "{FirebaseArgument.get_flag(FirebaseArgument.PROJECT_NUMBER)}" instead.'
            )
            log.get_logger(cls).warning(cli.Colors.YELLOW(message))

        project_number = FirebaseArgument.PROJECT_NUMBER.from_args(cli_args)

        if not project_id and not project_number:
            raise FirebaseArgument.PROJECT_NUMBER.raise_argument_error()

        return FirebaseAppDistribution(
            credentials_argument.value,
            project_number=project_id or project_number,
            json_output=bool(cli_args.json_output),
            **cls._parent_class_kwargs(cli_args),
        )


if __name__ == "__main__":
    FirebaseAppDistribution.invoke_cli()
