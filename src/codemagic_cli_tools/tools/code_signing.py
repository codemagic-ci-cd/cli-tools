import argparse
import json
import pathlib
import shlex
import shutil
from tempfile import NamedTemporaryFile
from typing import Counter
from typing import Generator
from typing import Iterator
from typing import Optional
from typing import Sequence

from codemagic_cli_tools import cli
from codemagic_cli_tools.cli.colors import Colors
from codemagic_cli_tools.models import ProvisioningProfile
from .keychain import Keychain
from .mixins import PathFinderMixin


def _existing_file(path_str: str) -> pathlib.Path:
    path = pathlib.Path(path_str)
    if not path.exists():
        raise argparse.ArgumentTypeError(f'Path "{path}" does not exist')
    if not path.is_file():
        raise argparse.ArgumentTypeError(f'Path "{path}" is not a file')
    return path


class CodeSigningException(cli.CliAppException):
    pass


class CodeSigningArgument(cli.Argument):
    XCODE_PROJECT_PATTERN = cli.ArgumentProperties(
        key='xcode_project_patterns',
        flags=('--project',),
        type=pathlib.Path,
        description=(
            'Path to Xcode project (*.xcodeproj). Can be either a path literal, or '
            'a glob pattern to match projects in working directory.'
        ),
        argparse_kwargs={
            'required': False,
            'default': (pathlib.Path('**/*.xcodeproj'),),
            'nargs': '+',
            'metavar': 'project-path'
        },
    )
    PROFILE_PATHS = cli.ArgumentProperties(
        key='profile_path_patterns',
        flags=('--profile',),
        type=_existing_file,
        description=(
            'Path to provisioning profile. Can be either a path literal, or '
            'a glob pattern to match provisioning profiles.'
        ),
        argparse_kwargs={
            'required': False,
            'nargs': '+',
            'metavar': 'profile-path',
            'default': (ProvisioningProfile.DEFAULT_LOCATION,),
        }
    )


class CodeSigning(cli.CliApp, PathFinderMixin):
    """
    Utility to prepare iOS application code signing properties for build
    """

    @property
    def _code_signing_manager(self) -> str:
        if shutil.which('code_signing_manager.rb'):
            return 'code_signing_manager.rb'
        executable = pathlib.Path(__file__) / '..' / '..' / '..' / '..' / 'bin' / 'code_signing_manager.rb'
        return str(executable.resolve())

    @cli.action('use-profiles',
                CodeSigningArgument.XCODE_PROJECT_PATTERN,
                CodeSigningArgument.PROFILE_PATHS)
    def use_profiles(self,
                     xcode_project_patterns: Sequence[pathlib.Path],
                     profile_path_patterns: Sequence[pathlib.Path]):
        """
        Set up code signing settings on specified Xcode project
        to use given provisioning profiles.
        """

        profile_paths = self.find_paths(*profile_path_patterns)
        try:
            serialized_profiles = json.dumps(list(self._serialize_profiles(profile_paths)))
        except (ValueError, IOError) as error:
            raise CodeSigningException(*error.args)

        xcode_projects = self.find_paths(*xcode_project_patterns)
        for xcode_project in xcode_projects:
            used_profiles = self._use_profiles(xcode_project, serialized_profiles)
            # TODO: proper profile usage notice
            self.logger.info(Colors.GREEN(f'Use profiles result: {used_profiles}'))

    def _serialize_profiles(self, profile_paths: Iterator[pathlib.Path]) -> Generator:
        available_certs = Keychain(use_default=True) \
            .list_code_signing_certificates(should_print=False)

        for profile_path in profile_paths:
            profile = ProvisioningProfile.from_path(profile_path, cli_app=self)
            usable_certificates = profile.get_usable_certificates(available_certs)
            common_names = Counter[str](certificate.common_name for certificate in usable_certificates)
            most_popular_common = common_names.most_common(1)
            common_name = most_popular_common[0][0] if most_popular_common else ''
            yield {'certificate_common_name': common_name, **profile.dict()}

    def _use_profiles(self, xcode_project: pathlib.Path, json_serialized_profiles: str):
        with NamedTemporaryFile(mode='r', prefix='used_profiles_', suffix='.json') as used_profiles:
            cmd = [
                self._code_signing_manager,
                '--xcode-project', xcode_project,
                '--used-profiles', used_profiles.name,
                '--profiles', json_serialized_profiles,
            ]
            if self.verbose:
                cmd.append('--verbose')
            process = self.execute(cmd)
            try:
                used_profiles_info = json.load(used_profiles)
            except ValueError:
                self.logger.debug(f'Failed to read used profiles info from {used_profiles.name}')
                used_profiles_info = {}
        if process.returncode != 0:
            error = f'Failed to set code signing settings for {xcode_project}'
            raise CodeSigningException(error, process)
        return used_profiles_info


if __name__ == '__main__':
    CodeSigning.invoke_cli()
