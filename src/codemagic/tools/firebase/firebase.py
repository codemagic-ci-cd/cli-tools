#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json

from codemagic import cli
from codemagic.firebase.api_client import FirebaseApiClient

from .actions import GetLatestBuildVersionAction
from .arguments import FirebaseArgument


@cli.common_arguments(FirebaseArgument.FIREBASE_SERVICE_ACCOUNT_CREDENTIALS)
class Firebase(cli.CliApp, GetLatestBuildVersionAction):
    """
    Utility to get the latest build versions from Firebase using Firebase API
    """

    def __init__(self, credentials: dict, **kwargs):
        super().__init__(**kwargs)
        self.api_client = FirebaseApiClient(credentials)

    @classmethod
    def from_cli_args(cls, cli_args: argparse.Namespace) -> Firebase:
        credentials_argument = FirebaseArgument.FIREBASE_SERVICE_ACCOUNT_CREDENTIALS.from_args(cli_args)
        if credentials_argument is None:
            raise FirebaseArgument.FIREBASE_SERVICE_ACCOUNT_CREDENTIALS.raise_argument_error()

        return Firebase(
            json.loads(credentials_argument.value),
            **cls._parent_class_kwargs(cli_args),
        )


if __name__ == '__main__':
    Firebase.invoke_cli()
