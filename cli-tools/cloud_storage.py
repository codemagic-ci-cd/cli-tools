#!/usr/bin/env python3

import argparse
import json
import pathlib
import sys
from typing import NoReturn

from google.cloud import storage
from google.oauth2 import service_account

import cli


class CloudStorageError(cli.CliAppException):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


def _existing_path(path_str: str) -> pathlib.Path:
    path = pathlib.Path(path_str)
    if path.exists():
        return path
    raise argparse.ArgumentTypeError(f'Path "{path}" does not exist')


class CloudStorageArgument(cli.Argument):
    CREDENTIALS_PATH = cli.ArgumentProperties(
        key='credentials_path',
        type=_existing_path,
        description='Path to Cloud Storage service account json credentials',
    )
    BUCKET_NAME = cli.ArgumentProperties(
        key='bucket',
        flags=('--bucket',),
        argparse_kwargs={'default': 'secure.codemagic.io', 'required': False},
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


class CloudStorage(cli.CliApp):
    """
    Utility to download files from Google Cloud Storage
    """

    CLI_EXCEPTION_TYPE = CloudStorageError

    def __init__(self, credentials_path: pathlib.Path, bucket_name: str):
        super().__init__()
        self.credentials = json.loads(credentials_path.read_text())
        self.bucket_name = bucket_name
        self._bucket = None
        self._storage_client = None

    @classmethod
    def from_cli_args(cls, cli_args: argparse.Namespace) -> 'CloudStorage':
        credentials_path = getattr(cli_args, CloudStorageArgument.CREDENTIALS_PATH.value.key)
        default_bucket = CloudStorageArgument.BUCKET_NAME.get_default()
        bucket_name = getattr(cli_args, CloudStorageArgument.BUCKET_NAME.value.key, default_bucket)
        return CloudStorage(credentials_path, bucket_name)

    @cli.action('save-to-file',
                CloudStorageArgument.CREDENTIALS_PATH,
                CloudStorageArgument.BUCKET_NAME,
                CloudStorageArgument.OBJECT_NAME,
                CloudStorageArgument.SAVE_TO_LOCATION)
    def save_to_file(self, object_name: str, save_to_location: pathlib.Path):
        """
        Save specified object from Cloud Storage bucket to local disk
        """
        blob = self.get_blob(object_name)
        blob.download_to_filename(str(save_to_location))
        self.logger.info(f'Saved {object_name} to file {save_to_location}')

    @cli.action('show-contents',
                CloudStorageArgument.CREDENTIALS_PATH,
                CloudStorageArgument.BUCKET_NAME,
                CloudStorageArgument.OBJECT_NAME)
    def show_contents(self, object_name):
        """
        Print contents of specified object from Cloud Storage bucket
        to STDOUT
        """
        blob = self.get_blob(object_name)
        contents = blob.download_as_string()
        print(contents.decode())

    @property
    def storage_client(self) -> storage.Client:
        if self._storage_client is None:
            credentials = service_account.Credentials.from_service_account_info(self.credentials)
            self._storage_client = storage.Client(credentials=credentials, project=self.credentials['project_id'])
        return self._storage_client

    @property
    def bucket(self) -> storage.Bucket:
        if self._bucket is None:
            self._bucket = self.storage_client.bucket(self.bucket_name)
        return self._bucket

    def get_blob(self, object_name) -> storage.Blob:
        blob = self.bucket.blob(object_name)
        if blob.exists():
            return blob
        raise CloudStorageError(f'Missing GCloud object: "{object_name}" does not exist in bucket "{self.bucket_name}"')

    @classmethod
    def _handle_cli_exception(cls, cli_exception: CloudStorageError) -> NoReturn:
        sys.stderr.write(f'{cli_exception.message}\n')
        sys.exit(1)


if __name__ == '__main__':
    CloudStorage.invoke_cli()
