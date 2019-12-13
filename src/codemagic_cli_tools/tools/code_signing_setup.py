import argparse
import json
import os
import pathlib
import shlex
from tempfile import NamedTemporaryFile
from typing import Optional
from typing import Sequence

from codemagic_cli_tools import cli
from codemagic_cli_tools.models import ProvisioningProfile
from codemagic_cli_tools.cli.colors import Colors


def _existing_directory(path_str: str) -> pathlib.Path:
    path = pathlib.Path(path_str)
    if not path.exists():
        raise argparse.ArgumentTypeError(f'Path "{path}" does not exist')
    if not path.is_dir():
        raise argparse.ArgumentTypeError(f'Path "{path}" is not a directory')
    return path


def _existing_file(path_str: str) -> pathlib.Path:
    path = pathlib.Path(path_str)
    if not path.exists():
        raise argparse.ArgumentTypeError(f'Path "{path}" does not exist')
    if not path.is_file():
        raise argparse.ArgumentTypeError(f'Path "{path}" is not a file')
    return path


class CodeSigningSetupArgument(cli.Argument):
    WORKING_DIRECTORY = cli.ArgumentProperties(
        key='working_directory',
        flags=('--cwd',),
        type=_existing_directory,
        description='Working directory',
        argparse_kwargs={'required': False, 'default': '.'},
    )
    XCODE_PROJECT_PATTERN = cli.ArgumentProperties(
        key='xcode_project_pattern',
        flags=('--xcode-project-pattern',),
        type=pathlib.Path,
        description=(
            'Glob pattern to Xcode projects to apply the settings to,'
            'relative to working directory. Literal paths are valid too.'
        ),
        argparse_kwargs={'required': False, 'default': '**/*.xcodeproj'},
    )
    PROFILE_PATHS = cli.ArgumentProperties(
        key='profile_paths',
        flags=('--profiles',),
        type=_existing_file,
        description=(
            'Path to provisioning profile to be used for code signing. '
            f'If not provided, the profiles will be looked up from '
            f'{Colors.WHITE(shlex.quote(str(ProvisioningProfile.DEFAULT_LOCATION)))}.'
        ),
        argparse_kwargs={
            'required': False,
            'nargs': '+',
            'metavar': 'profile-path'
        }
    )


@cli.common_arguments(CodeSigningSetupArgument.WORKING_DIRECTORY)
class CodeSigningSetup(cli.CliApp):
    """
    Utility to prepare iOS application code signing properties for build
    """

    def __init__(self, working_directory: pathlib.Path = pathlib.Path('.')):
        super().__init__()
        os.chdir(str(working_directory))

    def _find_paths(self, pattern: pathlib.Path):
        if pattern.is_absolute():
            self.logger.info(f'Searching for files matching {pattern}')
            # absolute globs are not supported, match them as relative to root
            relative_pattern = pattern.relative_to(pattern.anchor)
            return pathlib.Path(pattern.anchor).glob(str(relative_pattern))
        self.logger.info(f'Searching for files matching {pattern.resolve()}')
        return pathlib.Path().glob(str(pattern))

    @cli.action('use-profiles',
                CodeSigningSetupArgument.XCODE_PROJECT_PATTERN,
                CodeSigningSetupArgument.PROFILE_PATHS
                )
    def use_profiles(self,
                     xcode_project_pattern: pathlib.Path,
                     profile_paths: Optional[Sequence[pathlib.Path]] = None):
        """
        Use specified provisioning profiles on given
        """
        if profile_paths is None:
            profile_paths = list(ProvisioningProfile.DEFAULT_LOCATION.glob('*.mobileprovision'))
        xcode_projects = list(self._find_paths(xcode_project_pattern))
        profiles = [ProvisioningProfile.from_path(profile_path) for profile_path in profile_paths][:1]
        # for profile in profiles:
        #     print(profile.name)

        from .keychain import Keychain
        available_certs = Keychain().list_code_signing_certificates()
        print(len(available_certs))
        return
        for xcode_project in xcode_projects:
            with NamedTemporaryFile(suffix='.json', delete=False) as tf:
                used_profiles = tf.name
            cmd = [
                'code_signing_manager.rb',
                '--xcode-project', xcode_project,
                '--used-profiles', used_profiles,
                '--profiles', json.dumps(profiles),
                '--verbose'
            ]
            print(cmd)


if __name__ == '__main__':
    CodeSigningSetup.invoke_cli()
