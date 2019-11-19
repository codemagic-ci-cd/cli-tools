#!/usr/bin/env python3

from __future__ import annotations

import argparse
import pathlib
from tempfile import NamedTemporaryFile

from . import cli

DEFAULT_BUCKET = 'secure.codemagic.io'


class ExplicateError(cli.CliAppException):
    pass


def _existing_path(path_str: str) -> pathlib.Path:
    path = pathlib.Path(path_str)
    if path.exists():
        return path
    raise argparse.ArgumentTypeError(f'Path "{path}" does not exist')


class ExplicateArgument(cli.Argument):
    BUCKET_NAME = cli.ArgumentProperties(
        key='bucket',
        flags=('--bucket',),
        argparse_kwargs={'default': DEFAULT_BUCKET, 'required': False},
        description='Name of the Cloud Storage bucket containing the object. For example, "my-bucket".',
    )
    OBJECT_NAME = cli.ArgumentProperties(
        key='object_name',
        description='Name of object you are interacting with. For example, "pets/dog.png".',
        is_action_kwarg=True,
    )
    SAVE_TO_LOCATION = cli.ArgumentProperties(
        key='save_to_location',
        type=pathlib.Path,
        description='Local path where you are saving your object. For example, "Desktop/Images".',
        is_action_kwarg=True
    )
    SILENT = cli.ArgumentProperties(
        key='silent',
        flags=('--silent',),
        type=bool,
        description='Turn off log output from gsutil',
        argparse_kwargs={'required': False, 'action': 'store_true'},
        is_action_kwarg=True
    )


class Explicate(cli.CliApp):
    """
    Utility to download files from Google Cloud Storage
    """

    def __init__(self, bucket_name: str = DEFAULT_BUCKET):
        super().__init__()
        self.bucket_name = bucket_name

    @classmethod
    def from_cli_args(cls, cli_args: argparse.Namespace) -> Explicate:
        default_bucket = ExplicateArgument.BUCKET_NAME.get_default()
        bucket_name = getattr(cli_args, ExplicateArgument.BUCKET_NAME.value.key, default_bucket)
        return Explicate(bucket_name)

    @cli.action('save-to-file',
                ExplicateArgument.BUCKET_NAME,
                ExplicateArgument.OBJECT_NAME,
                ExplicateArgument.SAVE_TO_LOCATION,
                ExplicateArgument.SILENT)
    def save_to_file(self, object_name: str, save_to_location: pathlib.Path, silent: bool = False) -> pathlib.Path:
        """
        Save specified object from Cloud Storage bucket to local disk
        """
        process = self.execute(
            ['gsutil', 'cp', f'gs://{self.bucket_name}/{object_name}', save_to_location], show_output=not silent)
        if process.returncode != 0:
            error = f'Unable to save file: "{object_name}" does not exist in bucket "{self.bucket_name}"'
            raise ExplicateError(error, process)
        return save_to_location

    @cli.action('show-contents',
                ExplicateArgument.BUCKET_NAME,
                ExplicateArgument.OBJECT_NAME,
                ExplicateArgument.SILENT)
    def show_contents(self, object_name, silent: bool = False) -> str:
        """
        Print contents of specified object from Cloud Storage bucket to STDOUT
        """
        with NamedTemporaryFile() as tf:
            process = self.execute(
                ['gsutil', 'cp', f'gs://{self.bucket_name}/{object_name}', tf.name], show_output=not silent)
            if process.returncode != 0:
                error = f'Unable to show contents: "{object_name}" does not exist in bucket "{self.bucket_name}"'
                raise ExplicateError(error, process)
            contents = open(tf.name).read()
            print(contents)
        return contents


if __name__ == '__main__':
    Explicate.invoke_cli()
