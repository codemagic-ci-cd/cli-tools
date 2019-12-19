import pathlib
from collections import defaultdict
from typing import Counter
from typing import List
from typing import Optional
from typing import Sequence

from codemagic_cli_tools import cli
from codemagic_cli_tools.cli import Colors
from codemagic_cli_tools.models import BundleIdDetector
from codemagic_cli_tools.models import CodeSigningSettingsManager
from codemagic_cli_tools.models import ProvisioningProfile
from .keychain import Keychain
from .mixins import PathFinderMixin


class XcodeProjectException(cli.CliAppException):
    pass


class XcodeProjectArgument(cli.Argument):
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
    PROFILE_PATHS = cli.ArgumentProperties(
        key='profile_path_patterns',
        flags=('--profile',),
        type=pathlib.Path,
        description=(
            'Path to provisioning profile. Can be either a path literal, or '
            'a glob pattern to match provisioning profiles.'
        ),
        argparse_kwargs={
            'required': False,
            'nargs': '+',
            'metavar': 'profile-path',
            'default': (ProvisioningProfile.DEFAULT_LOCATION / '*.mobileprovision',),
        }
    )


class XcodeProject(cli.CliApp, PathFinderMixin):
    """
    Utility to prepare iOS application code signing properties for build
    """

    @cli.action('detect-bundle-id',
                XcodeProjectArgument.XCODE_PROJECT_PATTERN,
                XcodeProjectArgument.TARGET_NAME,
                XcodeProjectArgument.CONFIGURATION_NAME)
    def detect_bundle_id(self,
                         xcode_project_patterns: Sequence[pathlib.Path],
                         target_name: Optional[str] = None,
                         configuration_name: Optional[str] = None,
                         include_pods: bool = False,
                         should_print: bool = True) -> str:
        """ Try to deduce the Bundle ID from specified Xcode project """

        xcode_projects = self.find_paths(*xcode_project_patterns)
        bundle_ids = Counter[str](
            bundle_id
            for xcode_project in xcode_projects
            for bundle_id in self._detect_project_bundle_ids(
                xcode_project, target_name, configuration_name, include_pods)
        )

        if not bundle_ids:
            raise XcodeProjectException(f'Unable to detect Bundle ID')
        bundle_id = bundle_ids.most_common(1)[0][0]

        self.logger.info(Colors.GREEN(f'Chose Bundle ID {bundle_id}'))
        if should_print:
            print(bundle_id)
        return bundle_id

    def _detect_project_bundle_ids(self,
                                   xcode_project: pathlib.Path,
                                   target_name: Optional[str],
                                   config_name: Optional[str],
                                   include_pods: bool) -> List[str]:

        def group(bundle_ids):
            groups = defaultdict(list)
            for bundle_id in bundle_ids:
                groups['$' in bundle_id].append(bundle_id)
            return groups[True], groups[False]

        if not include_pods and xcode_project.stem == 'Pods':
            self.logger.info(f'Skip Bundle ID detection from Pod project {xcode_project}')
            return []

        detector = BundleIdDetector(xcode_project, target_name, config_name)
        detector.notify(self.logger)
        try:
            detected_bundle_ids = detector.detect(cli_app=self)
        except (ValueError, IOError) as error:
            raise XcodeProjectException(*error.args)

        env_var_bundle_ids, valid_bundle_ids = group(detected_bundle_ids)
        if env_var_bundle_ids:
            msg = f'Bundle IDs {", ".join(env_var_bundle_ids)} contain environment variables, exclude them.'
            self.logger.info(Colors.YELLOW(msg))
        self.logger.info(f'Detected Bundle IDs: {", ".join(valid_bundle_ids)}')
        return valid_bundle_ids

    @cli.action('use-profiles',
                XcodeProjectArgument.XCODE_PROJECT_PATTERN,
                XcodeProjectArgument.PROFILE_PATHS)
    def use_profiles(self,
                     xcode_project_patterns: Sequence[pathlib.Path],
                     profile_path_patterns: Sequence[pathlib.Path]):
        """
        Set up code signing settings on specified Xcode projects
        to use given provisioning profiles
        """

        self.logger.info('Configure code signing settings')

        profile_paths = self.find_paths(*profile_path_patterns)
        xcode_projects = self.find_paths(*xcode_project_patterns)

        try:
            profiles = [ProvisioningProfile.from_path(p, cli_app=self) for p in profile_paths]
        except (ValueError, IOError) as error:
            raise XcodeProjectException(*error.args)

        available_certs = Keychain().list_code_signing_certificates(should_print=False)
        code_signing_settings_manager = CodeSigningSettingsManager(profiles, available_certs)

        try:
            for xcode_project in xcode_projects:
                code_signing_settings_manager.use_profiles(xcode_project, cli_app=self)
        except (ValueError, IOError) as error:
            raise XcodeProjectException(*error.args)

        code_signing_settings_manager.notify_profile_usage(self.logger)


if __name__ == '__main__':
    XcodeProject.invoke_cli()
