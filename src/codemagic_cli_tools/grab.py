#!/usr/bin/env python3

import argparse
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List, Dict

from . import cli
from . import models


class GrabError(cli.CliAppException):
    pass


class Source(cli.EnumArgumentValue):
    codemagic = 'codemagic'
    apple_developer = 'apple_developer'


class AppleDeveloperToken(cli.EnvironmentArgumentValue):
    pass


class GrabArgument(cli.Argument):
    SOURCE = cli.ArgumentProperties(
        key='source',
        type=Source,
        description='Where to download the signing files from',
        argparse_kwargs={'choices': [source for source in Source]},
    )
    APPLE_DEVELOPER_TOKEN = cli.ArgumentProperties(
        key='apple_developer_token',
        flags=('-t', '--token'),
        type=AppleDeveloperToken,
        description='Apple Developer Portal API Token',
        argparse_kwargs={'required': True},
    )
    BUNDLE_IDENTIFIER = cli.ArgumentProperties(
        key='bundle_identifier',
        flags=('--bundle-identifier',),
        description='Bundle identifier for which the signing files will be downloaded',
        argparse_kwargs={'required': True},
    )
    CERTIFICATES_DIRECTORY = cli.ArgumentProperties(
        key='certificates_directory',
        flags=('--certificates-dir',),
        type=Path,
        description='Directory where the code signing certificates will be saved',
        argparse_kwargs={'required': False, 'default': models.Certificate.DEFAULT_LOCATION},
    )
    PROFILES_DIRECTORY = cli.ArgumentProperties(
        key='profiles_directory',
        flags=('--profiles-dir',),
        type=Path,
        description='Directory where the provisioning profiles will be saved',
        argparse_kwargs={'required': False, 'default': models.ProvisioningProfile.DEFAULT_LOCATION},
    )


class Grab(cli.CliApp):
    """
    Utility to download code signing certificates and provisioning profiles
    to perform iOS code signing.
    """

    def __init__(self):
        super().__init__()

    @classmethod
    def from_cli_args(cls, cli_args: argparse.Namespace):
        return Grab()

    @cli.action('apple-developer',
                GrabArgument.APPLE_DEVELOPER_TOKEN,
                GrabArgument.BUNDLE_IDENTIFIER,
                GrabArgument.CERTIFICATES_DIRECTORY,
                GrabArgument.PROFILES_DIRECTORY)
    def fetch_from_apple_developer(self,
                                   apple_developer_token: AppleDeveloperToken,
                                   bundle_identifier: str,
                                   profiles_directory: Path,
                                   certificates_directory: Path):
        """
        Fetch code signing files from Apple Developer portal for
        specified bundle identifier
        """
        # TODO Apple Developer Portal communication
        raise NotImplemented

    @cli.action('codemagic', GrabArgument.CERTIFICATES_DIRECTORY, GrabArgument.PROFILES_DIRECTORY)
    def fetch_from_codemagic(self, profiles_directory: Path, certificates_directory: Path):
        """
        Fetch manual code signing files from Codemagic
        """
        signing_files_info = self._get_manual_signing_files_info()
        self._fetch_profiles_from_codemagic(signing_files_info['provisioning_profiles'], profiles_directory)
        self._fetch_certificates_from_codemagic(signing_files_info['code_signing_certificates'], certificates_directory)

    def _get_manual_signing_files_info(self) -> Dict[str, List[Dict]]:
        raw_info = os.environ.get('_MANUAL_SIGNING_FILES')
        if not raw_info:
            raise GrabError('Cannot fetch signing files from Codemagic: signing files information is not available')
        try:
            signing_files_info = json.loads(raw_info)
        except ValueError:
            self.logger.warning('Could not parse signing files info from %s', raw_info)
            raise GrabError('Cannot fetch signing files from Codemagic: signing files information is in invalid format')
        for key in ('provisioning_profiles', 'code_signing_certificates'):
            if key in signing_files_info:
                continue
            missing_entry = key.replace("_", " ")
            self.logger.warning(f'{missing_entry.capitalize()} are missing from signing files info {raw_info}')
            raise GrabError(
                f'Cannot fetch signing files from Codemagic: signing files information do not contain {missing_entry}')
        return signing_files_info

    def _fetch_profiles_from_codemagic(self, profiles_info: List[Dict], destination: Path) -> List[Path]:
        from .storage import Storage
        storage = Storage()
        destination.mkdir(exist_ok=True)
        save_paths = []
        for profile_info in profiles_info:
            filename = Path(profile_info['file_name'])
            self.logger.info(f'Fetch provisioning profile {filename} from Codemagic')
            tf = NamedTemporaryFile(prefix=f'{filename.stem}_', suffix=filename.suffix, dir=destination, delete=False)
            tf.close()
            storage.save_to_file(profile_info['object_name'], tf.name, silent=True)
            self.logger.info(f'Saved provisioning profile {filename} to {tf.name}')
            save_paths.append(Path(tf.name))
        return save_paths

    def _fetch_certificates_from_codemagic(self, certificates_info: List[Dict], destination: Path) -> List[Path]:
        from .storage import Storage
        storage = Storage()
        destination.mkdir(exist_ok=True)
        save_paths = []
        for certificate_info in certificates_info:
            filename = Path(certificate_info['file_name'])
            self.logger.info(f'Fetch certificate {filename} from Codemagic')
            tf = NamedTemporaryFile(prefix=f'{filename.stem}_', suffix=filename.suffix, dir=destination, delete=False)
            tf.close()
            storage.save_to_file(certificate_info['object_name'], tf.name, silent=True)
            password = certificate_info.get('password', None)
            if password:
                storage.save_to_file(password['object_name'], Path(f'{tf.name}.password'), silent=True)
            self.logger.info(f'Saved certificate {filename} to {tf.name}')
            save_paths.append(Path(tf.name))
        return save_paths


if __name__ == '__main__':
    Grab.invoke_cli()
