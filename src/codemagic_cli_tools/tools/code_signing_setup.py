import argparse
import enum
import json
import logging
import os
import pathlib
import shlex
import shutil
from collections import Counter
from tempfile import NamedTemporaryFile
from typing import Generator
from typing import Optional
from typing import Sequence

from codemagic_cli_tools import cli
from codemagic_cli_tools.cli.colors import Colors
from codemagic_cli_tools.models import PbxProject
from codemagic_cli_tools.models import ProvisioningProfile
from .keychain import Keychain

AUTO_DETECT_BUNDLE_ID = 'auto-detect'


class ProvisioningMode(enum.Enum):
    automatic = 'automatic'
    manual = 'manual'

    def __str__(self):
        return str(self.value)


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


class CodeSigningSetupException(cli.CliAppException):
    pass


class CodeSigningSetupArgument(cli.Argument):
    WORKING_DIRECTORY = cli.ArgumentProperties(
        key='working_directory',
        flags=('--cwd',),
        type=_existing_directory,
        description='Working directory',
        argparse_kwargs={'required': False, 'default': '.'},
    )
    JSON_OUTPUT = cli.ArgumentProperties(
        key='json_output',
        flags=('--json',),
        type=bool,
        description='Whether to show the resource in JSON format',
        argparse_kwargs={'required': False, 'action': 'store_true'},
    )
    PROVISIONING_MODE = cli.ArgumentProperties(
        key='provisioning_mode',
        type=ProvisioningMode,
        description=(
            'Whether to use manually uploaded signing files or '
            'download them automatically from Apple Developer Portal.'
        ),
        argparse_kwargs={'choices': list(ProvisioningMode)}
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
    XCODE_PROJECT_PATH = cli.ArgumentProperties(
        key='xcode_project_path',
        type=pathlib.Path,
        description='Path to Xcode project (*.xcodeproj)',
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
    TARGET_NAME = cli.ArgumentProperties(
        key='target_name',
        flags=('--target',),
        description='Name of the build target',
        argparse_kwargs={'required': False},
    )
    CONFIGURATION_NAME = cli.ArgumentProperties(
        key='configuration_name',
        flags=('--config',),
        description='Name of the build configuration',
        argparse_kwargs={'required': False},
    )
    AUTOMATIC_PROVISIONING_BUNDLE_ID = cli.ArgumentProperties(
        key='bundle_id',
        flags=('--bundle-id',),
        description='Name of the build configuration',
        argparse_kwargs={'required': False, 'default': AUTO_DETECT_BUNDLE_ID},
    )


@cli.common_arguments(
    CodeSigningSetupArgument.WORKING_DIRECTORY,
    CodeSigningSetupArgument.JSON_OUTPUT
)
class CodeSigningSetup(cli.CliApp):
    """
    Utility to prepare iOS application code signing properties for build
    """

    def __init__(self, working_directory: pathlib.Path = pathlib.Path('.'), json_output: bool = False):
        super().__init__()
        os.chdir(str(working_directory))
        self.printer = Printer(self.logger, bool(json_output))

    def _find_paths(self, pattern: pathlib.Path) -> Generator[pathlib.Path, None, None]:
        if pattern.is_absolute():
            self.logger.info(f'Searching for files matching {pattern}')
            # absolute globs are not supported, match them as relative to root
            relative_pattern = pattern.relative_to(pattern.anchor)
            return pathlib.Path(pattern.anchor).glob(str(relative_pattern))
        self.logger.info(f'Searching for files matching {pattern.resolve()}')
        return pathlib.Path().glob(str(pattern))

    @property
    def _code_signing_manager(self) -> str:
        if shutil.which('code_signing_manager.rb'):
            return 'code_signing_manager.rb'
        executable = pathlib.Path(__file__) / '..' / '..' / '..'/ '..' / 'bin' / 'code_signing_manager.rb'
        return executable.resolve()

    @cli.action('use-profiles',
                CodeSigningSetupArgument.XCODE_PROJECT_PATH,
                CodeSigningSetupArgument.PROFILE_PATHS
                )
    def use_profiles(self,
                     xcode_project_path: pathlib.Path,
                     profile_paths: Optional[Sequence[pathlib.Path]] = None):
        """
        Use specified provisioning profiles on given
        """
        if profile_paths is None:
            profile_paths = list(ProvisioningProfile.DEFAULT_LOCATION.glob('*.mobileprovision'))

        available_certs = Keychain().list_code_signing_certificates(should_print=False)

        with NamedTemporaryFile(suffix='.json', delete=False) as tf:
            used_profiles = tf.name
        cmd = [
            self._code_signing_manager,
            '--xcode-project', xcode_project_path,
            '--used-profiles', used_profiles,
            '--profiles', json.dumps([
                ProvisioningProfile.from_path(profile_path).serialize_for_code_signing_manager(available_certs)
                for profile_path in profile_paths
            ]),
            '--verbose'
        ]
        print(cmd)
        # TODO: invoke code signing manager

    @cli.action('detect-bundle-id',
                CodeSigningSetupArgument.XCODE_PROJECT_PATH,
                CodeSigningSetupArgument.TARGET_NAME,
                CodeSigningSetupArgument.CONFIGURATION_NAME)
    def detect_bundle_id(self,
                         xcode_project_path: pathlib.Path,
                         target_name: Optional[str] = None,
                         configuration_name: Optional[str] = None,
                         should_print: bool = True) -> Optional[str]:
        """ Detect Bundle ID from specified Xcode project """

        try:
            project = PbxProject.from_path(xcode_project_path.expanduser() / 'project.pbxproj')
        except (ValueError, EnvironmentError) as error:
            raise CodeSigningSetupException(str(error))

        def get_targets():
            if target_name:
                return [project.get_target(target_name)]
            return project.get_targets()

        def get_configs(target):
            if configuration_name:
                return [project.get_target_config(target['name'], configuration_name)]
            return project.get_target_configs(target['name'])

        self.printer.log_detecting_bundle_id(xcode_project_path, target_name, configuration_name)
        try:
            bundle_ids = Counter(
                project.get_bundle_id(target['name'], config['name'])
                for target in get_targets()
                for config in get_configs(target)
            )
        except ValueError as ve:
            raise CodeSigningSetupException(str(ve))
        if not bundle_ids:
            xcode_project = shlex.quote(str(xcode_project_path))
            raise CodeSigningSetupException(f'Unable to detect Bundle ID from Xcode project {xcode_project}')

        self.logger.info(f'Detected Bundle IDs: {", ".join(bundle_ids)}')
        bundle_id = bundle_ids.most_common(1)[0][0]
        self.printer.print_object('Bundle ID', bundle_id, should_print)
        return bundle_id

    @cli.action('provision',
                CodeSigningSetupArgument.PROVISIONING_MODE,
                CodeSigningSetupArgument.XCODE_PROJECT_PATTERN,
                )
    def provision(self,
                  provisioning_mode: ProvisioningMode,
                  xcode_project_pattern: pathlib.Path,
                  bundle_id: str = 'auto-detect'):
        """
        Set up code signing for Xcode project
        """
        xcode_projects = list(self._find_paths(xcode_project_pattern))
        if not xcode_projects:
            raise CodeSigningSetupException(f'Did not find any Xcode project matching pattern {xcode_project_pattern}')

        __ = self._setup_keychain()
        if provisioning_mode is ProvisioningMode.automatic:
            self._automatic_provision(bundle_id, xcode_projects)
        elif provisioning_mode is ProvisioningMode.manual:
            self._manual_provision()
        else:
            raise CodeSigningSetupException(f'Invalid provisioning mode {provisioning_mode}')

        for xcode_project in xcode_projects:
            self.use_profiles(xcode_project)

    def _manual_provision(self):
        from .manual_provisioning import ManualProvisioning
        # ManualProvisioning().fetch()
        # TODO

    def _automatic_provision(self, bundle_id: str, xcode_projects: Sequence[pathlib.Path]):
        if bundle_id == AUTO_DETECT_BUNDLE_ID:
            bundle_ids = [self.detect_bundle_id(xcode_project) for xcode_project in xcode_projects]
            bundle_id = self.detect_bundle_id()
        # TODO

    @classmethod
    def _setup_keychain(cls):
        from .keychain import Keychain
        with NamedTemporaryFile(prefix='build_', suffix='.keychain') as tf:
            keychain_path = pathlib.Path(tf.name)
        return Keychain(keychain_path).initialize()


class Printer:

    def __init__(self, logger: logging.Logger, print_json: bool):
        self.print_json = print_json
        self.logger = logger

    def log_detecting_bundle_id(self, project_path: pathlib.Path, target: Optional[str], configuration: Optional[str]):
        prefix = f'Detect Bundle ID from {project_path}'
        if target and configuration:
            self.logger.info(f'{prefix} target {target!r} [{configuration!r}]')
        elif target:
            self.logger.info(f'{prefix} target {target!r}')
        elif configuration:
            self.logger.info(f'{prefix} build configuration {configuration!r}')
        else:
            self.logger.info(prefix)

    def print_object(self, name, obj, should_print: bool):
        if should_print is not True:
            return
        if self.print_json:
            print(json.dumps({name: obj}))
        else:
            print(obj)


if __name__ == '__main__':
    CodeSigningSetup.invoke_cli()
