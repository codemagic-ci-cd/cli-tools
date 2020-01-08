#!/usr/bin/env python3

from __future__ import annotations

import argparse
import pathlib
from tempfile import NamedTemporaryFile
from typing import Sequence

from codemagic_cli_tools import cli

DEFAULT_BUCKET = 'secure.codemagic.io'


class StorageError(cli.CliAppException):
    pass


def _existing_path(path_str: str) -> pathlib.Path:
    path = pathlib.Path(path_str)
    if path.exists():
        return path
    raise argparse.ArgumentTypeError(f'Path "{path}" does not exist')


class StorageArgument(cli.Argument):
    BUCKET_NAME = cli.ArgumentProperties(
        key='bucket',
        flags=('--bucket',),
        argparse_kwargs={'default': DEFAULT_BUCKET, 'required': False},
        description='Name of the Cloud Storage bucket containing the object. For example, "my-bucket".',
    )
    OBJECT_NAME = cli.ArgumentProperties(
        key='object_name',
        description='Name of object you are interacting with. For example, "pets/dog.png".',
    )
    UPLOAD_CONTENT = cli.ArgumentProperties(
        key='upload_content',
        description='String content to be uploaded',
    )
    UPLOAD_PATH = cli.ArgumentProperties(
        key='upload_path',
        type=pathlib.Path,
        description='Local path to a file that is uploaded. For example, "Desktop/Images/image.png".',
    )
    SAVE_PATH = cli.ArgumentProperties(
        key='save_path',
        type=pathlib.Path,
        description='Local path where you are saving your object. For example, "Desktop/Images".',
    )


@cli.common_arguments(StorageArgument.BUCKET_NAME)
class Storage(cli.CliApp):
    """
    Utility to download files from Google Cloud Storage
    """

    def __init__(self, bucket_name: str = DEFAULT_BUCKET, **kwargs):
        super().__init__(**kwargs)
        self.bucket_name = bucket_name

    @classmethod
    def from_cli_args(cls, cli_args: argparse.Namespace) -> Storage:
        default_bucket = StorageArgument.BUCKET_NAME.get_default()
        bucket_name = StorageArgument.BUCKET_NAME.from_args(cli_args, default_bucket)
        return Storage(bucket_name, **cls._parent_class_kwargs(cli_args))

    @cli.action('save',
                StorageArgument.OBJECT_NAME,
                StorageArgument.SAVE_PATH)
    def save(self, object_name: str, save_path: pathlib.Path) -> pathlib.Path:
        """
        Save specified object from Cloud Storage bucket to local disk
        """
        self._invoke_gsutil(
            ['gsutil', 'cp', f'gs://{self.bucket_name}/{object_name}', save_path],
            f'Unable to save file: "{object_name}" does not exist in bucket "{self.bucket_name}"'
        )
        self.logger.info(f'Saved {object_name} to {save_path}')
        return save_path

    @cli.action('show', StorageArgument.OBJECT_NAME)
    def show(self, object_name) -> str:
        """
        Print contents of specified object from Cloud Storage bucket to STDOUT
        """
        with NamedTemporaryFile() as tf:
            self._invoke_gsutil(
                ['gsutil', 'cp', f'gs://{self.bucket_name}/{object_name}', tf.name],
                f'Unable to show contents: "{object_name}" does not exist in bucket "{self.bucket_name}"'
            )
            contents = open(tf.name).read()
        self.echo(contents)
        return contents

    @cli.action('upload-contents', StorageArgument.OBJECT_NAME, StorageArgument.UPLOAD_CONTENT)
    def upload(self, object_name: str, upload_content: str):
        """
        Uploads given contents to specified object in Cloud Storage bucket
        """
        with NamedTemporaryFile('w') as tf:
            tf.write(upload_content)
            tf.flush()
            self._invoke_gsutil(
                ['gsutil', 'cp', tf.name, f'gs://{self.bucket_name}/{object_name}'],
                f'Unable to upload contents to {object_name}'
            )
        self.logger.info(f'Uploaded contents to {object_name}')

    @cli.action('upload', StorageArgument.OBJECT_NAME, StorageArgument.UPLOAD_PATH)
    def upload_file(self, object_name: str, upload_path: pathlib.Path):
        """
        Uploads file from given path to specified object in Cloud Storage bucket
        """
        self._invoke_gsutil(
            ['gsutil', 'cp', upload_path, f'gs://{self.bucket_name}/{object_name}'],
            f'Unable to upload file {upload_path}'
        )
        self.logger.info(f'Uploaded {upload_path} to {object_name}')

    @cli.action('delete', StorageArgument.OBJECT_NAME)
    def delete(self, object_name: str):
        """
        Delete object with specified name from the bucket
        """
        self._invoke_gsutil(
            ['gsutil', 'rm', f'gs://{self.bucket_name}/{object_name}'],
            f'Unable to delete object {object_name}'
        )
        self.logger.info(f'Deleted {object_name}')

    def _invoke_gsutil(self, command_args: Sequence[cli.CommandArg], error_msg) -> cli.CliProcess:
        process = self.execute(command_args, show_output=False)
        if process.returncode != 0:
            raise StorageError(error_msg, process)
        return process


if __name__ == '__main__':
    Storage.invoke_cli()
