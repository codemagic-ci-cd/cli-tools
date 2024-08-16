#!/usr/bin/env python3

from __future__ import annotations

import argparse
from typing import Dict
from typing import Optional

from codemagic import cli
from codemagic.google.firebase_client import FirebaseClient

from .action_groups import ReleasesActionGroup
from .actions import GetLatestBuildVersionAction
from .arguments import FirebaseArgument


@cli.common_arguments(
    FirebaseArgument.PROJECT_ID,
    FirebaseArgument.PROJECT_NUMBER,
    FirebaseArgument.FIREBASE_SERVICE_ACCOUNT_CREDENTIALS,
)
class FirebaseAppDistribution(
    cli.CliApp,
    GetLatestBuildVersionAction,
    ReleasesActionGroup,
):
    """
    Utility to list releases and retrieve the latest release build version number from Firebase
    """

    def __init__(self, credentials: Dict, project_number: Optional[str], project_id: Optional[str], **kwargs):
        super().__init__(**kwargs)
        self.client = FirebaseClient(credentials)
        if not project_id and not project_number:
            raise FirebaseArgument.PROJECT_NUMBER.raise_argument_error()
        self._project_id = project_id
        self._project_number = project_number

    @property
    def project_number(self):
        if not self._project_number:
            message = (
                "Deprecation warning! "
                'Flag "--project-id" was deprecated in version 0.53.5 '
                "and is subject for removal in future releases. "
                'Use "--project-number" instead.'
            )
            self.logger.warning(cli.Colors.YELLOW(message))
            return self._project_id
        return self._project_number

    @classmethod
    def from_cli_args(cls, cli_args: argparse.Namespace) -> FirebaseAppDistribution:
        credentials_argument = FirebaseArgument.FIREBASE_SERVICE_ACCOUNT_CREDENTIALS.from_args(cli_args)
        if credentials_argument is None:
            raise FirebaseArgument.FIREBASE_SERVICE_ACCOUNT_CREDENTIALS.raise_argument_error()

        return FirebaseAppDistribution(
            credentials_argument.value,
            FirebaseArgument.PROJECT_NUMBER.from_args(cli_args),
            FirebaseArgument.PROJECT_ID.from_args(cli_args),
            **cls._parent_class_kwargs(cli_args),
        )


if __name__ == "__main__":
    FirebaseAppDistribution.invoke_cli()
