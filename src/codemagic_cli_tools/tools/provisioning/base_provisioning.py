#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import re
import tempfile

from codemagic_cli_tools import cli
from codemagic_cli_tools.models import Certificate
from codemagic_cli_tools.models import ProvisioningProfile
from .automatic_provisioning_arguments import ProvisioningArgument


@cli.common_arguments(
    ProvisioningArgument.CERTIFICATES_DIRECTORY,
    ProvisioningArgument.PROFILES_DIRECTORY)
class BaseProvisioning(cli.CliApp):

    # TODO: Remove this class

    def __init__(self,
                 profiles_directory: pathlib.Path = ProvisioningProfile.DEFAULT_LOCATION,
                 certificates_directory: pathlib.Path = Certificate.DEFAULT_LOCATION,
                 **kwargs):
        super().__init__(**kwargs)
        self.profiles_directory = profiles_directory
        self.certificates_directory = certificates_directory

    @classmethod
    def _get_unique_path(cls, file_name: str, destination: pathlib.Path) -> pathlib.Path:
        if destination.exists() and not destination.is_dir():
            raise ValueError(f'Destination {destination} is not a directory')
        destination.mkdir(parents=True, exist_ok=True)
        name = pathlib.Path(re.sub(r'[^\w.]', '_', file_name))
        tf = tempfile.NamedTemporaryFile(
            prefix=f'{name.stem}_', suffix=name.suffix, dir=destination, delete=False)
        tf.close()
        return pathlib.Path(tf.name)
