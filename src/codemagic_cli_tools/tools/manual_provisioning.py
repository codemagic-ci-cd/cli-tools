#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List
from typing import NewType
from typing import Optional
from typing import Sequence
from typing import Tuple

from codemagic_cli_tools import cli
from .base_provisioning import BaseProvisioning
from .storage import Storage

ObjectName = NewType('ObjectName', str)


class ManualProvisioningError(cli.CliAppException):
    pass


class ManualProvisioningArgument(cli.Argument):
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


class ManualProvisioning(BaseProvisioning):
    """
    Utility to download code signing certificates and provisioning profiles
    from Codemagic to perform iOS code signing.
    """

    def __init__(self, **kwargs):
        super(ManualProvisioning, self).__init__(**kwargs)
        self._storage = Storage()

    @cli.action('fetch',
                ManualProvisioningArgument.PROVISIONING_PROFILE_OBJECT_NAME,
                ManualProvisioningArgument.CERTIFICATE_OBJECT_NAME,
                ManualProvisioningArgument.CERTIFICATE_PASSWORD_OBJECT_NAME)
    def fetch(self,
              profile_names: List[ObjectName],
              certificate_name: ObjectName,
              certificate_password_name: Optional[ObjectName] = None) -> Tuple[List[Path], Path]:
        """
        Fetch manual code signing files from Codemagic
        """

        for profile_name in profile_names:
            if not profile_name:
                raise ManualProvisioningError(
                    f'Cannot fetch signing files from Codemagic: provisioning profile object name not given')
        if not certificate_name:
            raise ManualProvisioningError(
                f'Cannot fetch signing files from Codemagic: certificate object name not given')

        profile_paths = self._download_profiles(profile_names)
        certificate_path = self._download_certificate(certificate_name, certificate_password_name)
        return profile_paths, certificate_path

    def _download_profile(self, profile_name: str) -> Path:
        self.logger.info(f'Download provisioning profile {profile_name} from Codemagic')
        path = self._get_unique_path('profile.mobileprovision', self.profiles_directory)
        self._storage.save_to_file(profile_name, path, silent=True)
        self.logger.info(f'Saved provisioning profile {profile_name} to {path}')
        return path

    def _download_profiles(self, profiles: Sequence[ObjectName]) -> List[Path]:
        return [self._download_profile(p) for p in profiles]

    def _download_certificate(self, certificate_name: ObjectName, password_name: Optional[ObjectName]) -> Path:
        self.logger.info(f'Download certificate {certificate_name} from Codemagic')
        path = self._get_unique_path('certificate.p12', self.certificates_directory)
        self._storage.save_to_file(certificate_name, path, silent=True)
        if password_name:
            self._storage.save_to_file(password_name, Path(f'{path}.password'), silent=True)
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
    ManualProvisioning.invoke_cli()
