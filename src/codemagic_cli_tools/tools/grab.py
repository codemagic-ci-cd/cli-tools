#!/usr/bin/env python3

import logging
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List
from typing import NewType
from typing import Optional
from typing import Sequence
from typing import Tuple

from codemagic_cli_tools import cli
from codemagic_cli_tools.models import Certificate
from codemagic_cli_tools.models import ProvisioningProfile

ObjectName = NewType('ObjectName', str)


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
        argparse_kwargs={'required': False, 'default': Certificate.DEFAULT_LOCATION},
    )
    PROFILES_DIRECTORY = cli.ArgumentProperties(
        key='profiles_directory',
        flags=('--profiles-dir',),
        type=Path,
        description='Directory where the provisioning profiles will be saved',
        argparse_kwargs={'required': False, 'default': ProvisioningProfile.DEFAULT_LOCATION},
    )
    PROVISIONING_PROFILE_OBJECT_NAME = cli.ArgumentProperties(
        key='profile_names',
        flags=('--profile-names',),
        type=ObjectName,
        description='Name of provisioning profile object in Cloud Storage',
        argparse_kwargs={'required': True, 'nargs': '+', 'metavar': 'profile-object-name'},
    )
    CERTIFICATE_OBJECT_NAME = cli.ArgumentProperties(
        key='certificate_name',
        flags=('--certificate-name',),
        type=ObjectName,
        description='Name of certificate object in Cloud Storage',
        argparse_kwargs={'required': True, 'metavar': 'certificate-object-name'},
    )
    CERTIFICATE_PASSWORD_OBJECT_NAME = cli.ArgumentProperties(
        key='certificate_password_name',
        flags=('--certificate-password-name',),
        type=ObjectName,
        description='Name of certificate password object in Cloud Storage',
        argparse_kwargs={'required': False, 'metavar': 'certificate-password-object-name'},
    )


@cli.common_arguments(
    GrabArgument.PROFILES_DIRECTORY,
    GrabArgument.CERTIFICATES_DIRECTORY
)
class Grab(cli.CliApp):
    """
    Utility to download code signing certificates and provisioning profiles
    to perform iOS code signing.
    """

    def __init__(self,
                 profiles_directory: Path = ProvisioningProfile.DEFAULT_LOCATION,
                 certificates_directory: Path = Certificate.DEFAULT_LOCATION):
        super().__init__()
        self.profiles_directory = profiles_directory
        self.certificates_directory = certificates_directory

    @cli.action('apple-developer',
                GrabArgument.APPLE_DEVELOPER_TOKEN,
                GrabArgument.BUNDLE_IDENTIFIER)
    def fetch_from_apple_developer(self,
                                   apple_developer_token: AppleDeveloperToken,
                                   bundle_identifier: str):
        """
        Fetch code signing files from Apple Developer portal for
        specified bundle identifier
        """
        # TODO Apple Developer Portal communication
        raise NotImplemented

    @cli.action('codemagic',
                GrabArgument.PROVISIONING_PROFILE_OBJECT_NAME,
                GrabArgument.CERTIFICATE_OBJECT_NAME,
                GrabArgument.CERTIFICATE_PASSWORD_OBJECT_NAME)
    def fetch_from_codemagic(self,
                             profile_names: List[ObjectName],
                             certificate_name: ObjectName,
                             certificate_password_name: Optional[ObjectName] = None) -> Tuple[List[Path], Path]:
        """
        Fetch manual code signing files from Codemagic
        """

        for profile_name in profile_names:
            if not profile_name:
                raise GrabError(
                    f'Cannot fetch signing files from Codemagic: provisioning profile object name not given')
        if not certificate_name:
            raise GrabError(
                f'Cannot fetch signing files from Codemagic: certificate object name not given')

        downloader = _CodemagicDownloader(self.profiles_directory, self.certificates_directory)
        profile_paths = downloader.download_profiles(profile_names)
        certificate_path = downloader.download_certificate(certificate_name, certificate_password_name)
        return profile_paths, certificate_path


class _CodemagicDownloader:

    def __init__(self, profiles_directory: Path, certificates_directory: Path):
        from .storage import Storage
        self.storage = Storage()
        self.profiles_directory = profiles_directory
        self.certificates_directory = certificates_directory
        self.logger = logging.getLogger(self.__class__.__name__)

    def _download_profile(self, profile_name: str) -> Path:
        self.logger.info(f'Download provisioning profile {profile_name} from Codemagic')
        path = self._get_unique_path('profile.mobileprovision', self.profiles_directory)
        self.storage.save_to_file(profile_name, path, silent=True)
        self.logger.info(f'Saved provisioning profile {profile_name} to {path}')
        return path

    def download_profiles(self, profiles: Sequence[ObjectName]) -> List[Path]:
        return [self._download_profile(p) for p in profiles]

    def download_certificate(self, certificate_name: ObjectName, password_name: Optional[ObjectName]) -> Path:
        self.logger.info(f'Download certificate {certificate_name} from Codemagic')
        path = self._get_unique_path('certificate.p12', self.certificates_directory)
        self.storage.save_to_file(certificate_name, path, silent=True)
        if password_name:
            self.storage.save_to_file(password_name, Path(f'{path}.password'), silent=True)
        self.logger.info(f'Saved certificate {certificate_name} to {path}')
        return path

    @classmethod
    def _get_unique_path(cls, file_name: str, destination: Path) -> Path:
        if destination.exists() and not destination.is_dir():
            raise ValueError(f'Destination {destination} is not a directory')
        destination.mkdir(parents=True, exist_ok=True)
        name = Path(file_name)
        tf = NamedTemporaryFile(prefix=f'{name.stem}_', suffix=name.suffix, dir=destination, delete=False)
        tf.close()
        return Path(tf.name)


if __name__ == '__main__':
    Grab.invoke_cli()
