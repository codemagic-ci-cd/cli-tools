#!/usr/bin/env python3
from __future__ import annotations

import pathlib

from codemagic_cli_tools import cli
from codemagic_cli_tools.models import Certificate
from codemagic_cli_tools.models import ProvisioningProfile


class ProvisioningArgument(cli.Argument):
    CERTIFICATES_DIRECTORY = cli.ArgumentProperties(
        key='certificates_directory',
        flags=('--certificates-dir',),
        type=pathlib.Path,
        description='Directory where the code signing certificates will be saved',
        argparse_kwargs={'required': False, 'default': Certificate.DEFAULT_LOCATION},
    )
    PROFILES_DIRECTORY = cli.ArgumentProperties(
        key='profiles_directory',
        flags=('--profiles-dir',),
        type=pathlib.Path,
        description='Directory where the provisioning profiles will be saved',
        argparse_kwargs={'required': False, 'default': ProvisioningProfile.DEFAULT_LOCATION},
    )


@cli.common_arguments(
    ProvisioningArgument.CERTIFICATES_DIRECTORY,
    ProvisioningArgument.PROFILES_DIRECTORY)
class BaseProvisioning(cli.CliApp):

    def __init__(self,
                 profiles_directory: pathlib.Path = ProvisioningProfile.DEFAULT_LOCATION,
                 certificates_directory: pathlib.Path = Certificate.DEFAULT_LOCATION):
        super().__init__()
        self.profiles_directory = profiles_directory
        self.certificates_directory = certificates_directory
