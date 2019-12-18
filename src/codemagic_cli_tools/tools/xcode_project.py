import pathlib
from typing import Counter
from typing import DefaultDict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple

from codemagic_cli_tools import cli
from codemagic_cli_tools.cli import Colors
from codemagic_cli_tools.models.bundle_id_detector import BundleIdDetector
from .mixins import PathFinderMixin


class XcodeProjectException(cli.CliAppException):
    pass


class XcodeProjectArgument(cli.Argument):
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


class XcodeProject(cli.CliApp, PathFinderMixin):
    """
    Utility to prepare iOS application code signing properties for build
    """

    @cli.action('detect-bundle-id',
                XcodeProjectArgument.XCODE_PROJECT_PATTERN,
                XcodeProjectArgument.TARGET_NAME,
                XcodeProjectArgument.CONFIGURATION_NAME)
    def detect_bundle_id(self,
                         xcode_project_pattern: pathlib.Path,
                         target_name: Optional[str] = None,
                         configuration_name: Optional[str] = None,
                         include_pods: bool = False,
                         should_print: bool = True) -> str:
        """ Try to deduce the Bundle ID from specified Xcode project """

        xcode_projects = self._find_paths(xcode_project_pattern.expanduser())
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

        if not include_pods and xcode_project.stem == 'Pods':
            self.logger.info(f'Skip Bundle ID detection from Pod project {xcode_project}')
            return []

        detector = BundleIdDetector(xcode_project, target_name, config_name)
        detector.notify(self.logger)
        try:
            bundle_ids = detector.detect(cli_app=self)
        except (ValueError, IOError) as error:
            raise XcodeProjectException(*error.args)

        env_var_bundle_ids, valid_bundle_ids = self._group_bundle_ids(bundle_ids)
        if env_var_bundle_ids:
            msg = f'Bundle IDs {", ".join(env_var_bundle_ids)} contain environment variables, exclude them.'
            self.logger.info(Colors.YELLOW(msg))
        self.logger.info(f'Detected Bundle IDs: {", ".join(valid_bundle_ids)}')
        return valid_bundle_ids

    @classmethod
    def _group_bundle_ids(cls, bundle_ids: Sequence[str]) -> Tuple[List[str], List[str]]:
        groups = DefaultDict[bool, List[str]](list)
        for bundle_id in bundle_ids:
            groups['$' in bundle_id].append(bundle_id)
        return groups[True], groups[False]
