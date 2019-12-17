import argparse
import json
import logging
import os
import pathlib
import shlex
import shutil
from tempfile import NamedTemporaryFile
from typing import Counter
from typing import Generator
from typing import List
from typing import Optional
from typing import Sequence

from codemagic_cli_tools import cli
from codemagic_cli_tools.cli.colors import Colors
from codemagic_cli_tools.models import BundleIdDetector
from codemagic_cli_tools.models import ProvisioningProfile
from .keychain import Keychain

AUTO_DETECT_BUNDLE_ID = 'auto-detect'


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
    XCODE_PROJECT_PATTERN = cli.ArgumentProperties(
        key='xcode_project_pattern',
        flags=('--xcode-project-pattern',),
        type=pathlib.Path,
        description=(
            'Glob pattern to detect Xcode projects for which to apply the settings to, '
            'relative to working directory. Can be a literal path.'
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
    CodeSigningSetupArgument.JSON_OUTPUT)
class CodeSigningSetup(cli.CliApp):
    """
    Utility to prepare iOS application code signing properties for build
    """

    def __init__(self, working_directory: pathlib.Path = pathlib.Path('.'), json_output: bool = False):
        super().__init__()
        os.chdir(str(working_directory))
        self.printer = Printer(self.logger, bool(json_output))

    @property
    def _code_signing_manager(self) -> str:
        if shutil.which('code_signing_manager.rb'):
            return 'code_signing_manager.rb'
        executable = pathlib.Path(__file__) / '..' / '..' / '..' / '..' / 'bin' / 'code_signing_manager.rb'
        return str(executable.resolve())

    @cli.action('use-profiles',
                CodeSigningSetupArgument.XCODE_PROJECT_PATH,
                CodeSigningSetupArgument.PROFILE_PATHS)
    def use_profiles(self,
                     xcode_project_path: pathlib.Path,
                     profile_paths: Optional[Sequence[pathlib.Path]] = None):
        """
        Set up code signing settings on specified Xcode project
        to use given provisioning profiles.
        """
        if profile_paths is None:
            profile_paths = list(ProvisioningProfile.DEFAULT_LOCATION.glob('*.mobileprovision'))

        with NamedTemporaryFile(suffix='.json', delete=False) as tf:
            used_profiles = tf.name

        try:
            serialized_profiles = list(self._serialize_profiles(profile_paths))
        except (ValueError, IOError) as error:
            raise CodeSigningSetupException(*error.args)

        cmd = [
            self._code_signing_manager,
            '--xcode-project', xcode_project_path,
            '--used-profiles', used_profiles,
            '--profiles', json.dumps(serialized_profiles),
            '--verbose'
        ]
        print(cmd)
        # TODO: invoke code signing manager

    def _serialize_profiles(self, profile_paths: Sequence[pathlib.Path]) -> Generator:
        available_certs = Keychain(use_default=True) \
            .list_code_signing_certificates(should_print=False)

        for profile_path in profile_paths:
            profile = ProvisioningProfile.from_path(profile_path, cli_app=self)
            usable_certificates = profile.get_usable_certificates(available_certs)
            common_names = Counter[str](certificate.common_name for certificate in usable_certificates)
            most_popular_common = common_names.most_common(1)
            common_name = most_popular_common[0][0] if most_popular_common else ''
            yield {'certificate_common_name': common_name, **profile.dict()}

    @cli.action('detect-bundle-id',
                CodeSigningSetupArgument.XCODE_PROJECT_PATH,
                CodeSigningSetupArgument.TARGET_NAME,
                CodeSigningSetupArgument.CONFIGURATION_NAME)
    def detect_bundle_id(self,
                         xcode_project_path: pathlib.Path,
                         target_name: Optional[str] = None,
                         configuration_name: Optional[str] = None,
                         should_print: bool = True) -> str:
        """ Detect Bundle ID from specified Xcode project """

        self.printer.log_detecting_bundle_id(xcode_project_path, target_name, configuration_name)
        detector = BundleIdDetector(xcode_project_path)
        try:
            bundle_ids = detector.detect(target_name, configuration_name, cli_app=self)
        except (ValueError, IOError) as error:
            raise CodeSigningSetupException(*error.args)

        if not bundle_ids:
            xcode_project = shlex.quote(str(xcode_project_path))
            raise CodeSigningSetupException(f'Unable to detect Bundle ID from Xcode project {xcode_project}')

        self.logger.info(f'Detected Bundle IDs: {", ".join(bundle_ids)}')
        bundle_id = bundle_ids.most_common(1)[0][0]
        self.printer.print_object('Bundle ID', bundle_id, should_print)
        return bundle_id

    def _autodetect_bundle_id(self, xcode_projects: Sequence[pathlib.Path]) -> str:
        self.logger.info('Autodetect Bundle ID for found Xcode projects')
        bundle_ids = Counter[str]()
        for xcode_project in xcode_projects:
            if xcode_project.stem == 'Pods':
                self.logger.info(f'Skip Bundle ID detection from Pod project {xcode_project}')
                continue
            bundle_id = self.detect_bundle_id(xcode_project, should_print=False)
            bundle_ids[bundle_id] += 1

        bundle_id = bundle_ids.most_common(1)[0][0]
        self.logger.info(Colors.GREEN(f'Detected Bundle ID {bundle_id}'))

        if '$' in bundle_id:
            raise CodeSigningSetupException(
                f'Detected Bundle ID "{bundle_id}" contains environment variables. '
                f'Please manually specify your Bundle ID with '
                f'{Colors.CYAN(CodeSigningSetupArgument.AUTOMATIC_PROVISIONING_BUNDLE_ID.key)}.'
            )
        return bundle_id

    @cli.action('automatic',
                CodeSigningSetupArgument.XCODE_PROJECT_PATTERN,
                CodeSigningSetupArgument.AUTOMATIC_PROVISIONING_BUNDLE_ID)
    def provision_automatic(self,
                            xcode_project_pattern: pathlib.Path,
                            bundle_id: str = 'auto-detect', ):
        """
        Set up code signing for Xcode project by fetching signing files
        automatically from Apple Developer Portal
        """
        xcode_projects = self._find_xcode_projects(xcode_project_pattern.expanduser())
        if bundle_id == AUTO_DETECT_BUNDLE_ID:
            bundle_id = self._autodetect_bundle_id(xcode_projects)

        # self._setup_keychain()
        # TODO: complete

    @cli.action('manual',
                CodeSigningSetupArgument.XCODE_PROJECT_PATTERN, )
    def provision_manual(self,
                         xcode_project_pattern: pathlib.Path):
        """
        Set up code signing for Xcode project by using signing files
        that were uploaded to Codemagic
        """
        xcode_projects = self._find_xcode_projects(xcode_project_pattern)
        self._setup_keychain()
        # from .manual_provisioning import ManualProvisioning
        # ManualProvisioning().fetch()
        # TODO
        for xcode_project in xcode_projects:
            self.use_profiles(xcode_project)

    def _find_paths(self, pattern: pathlib.Path) -> Generator[pathlib.Path, None, None]:
        if pattern.is_absolute():
            self.logger.info(f'Searching for files matching {pattern}')
            # absolute globs are not supported, match them as relative to root
            relative_pattern = pattern.relative_to(pattern.anchor)
            return pathlib.Path(pattern.anchor).glob(str(relative_pattern))
        self.logger.info(f'Searching for files matching {pattern.resolve()}')
        return pathlib.Path().glob(str(pattern))

    def _find_xcode_projects(self, xcode_project_pattern: pathlib.Path) -> List[pathlib.Path]:
        xcode_projects = list(self._find_paths(xcode_project_pattern))
        if not xcode_projects:
            error = f'Did not find any Xcode project matching pattern {xcode_project_pattern}'
            raise CodeSigningSetupException(error)
        return xcode_projects

    def _setup_keychain(self):
        with NamedTemporaryFile(prefix='build_', suffix='.keychain') as tf:
            keychain_path = pathlib.Path(tf.name)
        self.logger.info(f'Create new keychain to store code signing certificates at {keychain_path}')
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
            key = name.title().replace(' ', '')
            key = key[:1].lower() + key[1:]
            print(json.dumps({key: obj}))
        else:
            print(obj)


if __name__ == '__main__':
    CodeSigningSetup.invoke_cli()
