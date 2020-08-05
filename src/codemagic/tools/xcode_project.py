#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import shutil
from collections import defaultdict
from typing import Counter
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence

from codemagic import cli
from codemagic.cli import Colors
from codemagic.mixins import PathFinderMixin
from codemagic.models import BundleIdDetector
from codemagic.models import Certificate
from codemagic.models import CodeSigningSettingsManager
from codemagic.models import ExportOptions
from codemagic.models import ProvisioningProfile
from codemagic.models import Xcodebuild
from codemagic.models import Xcpretty


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
    XCODE_PROJECT_PATH = cli.ArgumentProperties(
        key='xcode_project_path',
        flags=('--project',),
        type=cli.CommonArgumentTypes.existing_path,
        description='Path to Xcode project (*.xcodeproj)',
        argparse_kwargs={'required': False}
    )
    XCODE_WORKSPACE_PATH = cli.ArgumentProperties(
        key='xcode_workspace_path',
        flags=('--workspace',),
        type=cli.CommonArgumentTypes.existing_path,
        description='Path to Xcode workspace (*.xcworkspace)',
        argparse_kwargs={'required': False}
    )
    SCHEME_NAME = cli.ArgumentProperties(
        key='scheme_name',
        flags=('--scheme',),
        description='Name of the Xcode Scheme',
        argparse_kwargs={'required': False},
    )
    TARGET_NAME = cli.ArgumentProperties(
        key='target_name',
        flags=('--target',),
        description='Name of the Xcode Target',
        argparse_kwargs={'required': False},
    )
    CONFIGURATION_NAME = cli.ArgumentProperties(
        key='configuration_name',
        flags=('--config',),
        description='Name of the Xcode build configuration',
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
    EXPORT_OPTIONS_PATH = cli.ArgumentProperties(
        key='export_options_plist',
        flags=('--export-options-plist',),
        type=pathlib.Path,
        description='Path to the generated export options plist',
        argparse_kwargs={
            'required': False,
            'default': pathlib.Path('~/export_options.plist').expanduser()
        }
    )
    ARCHIVE_DIRECTORY = cli.ArgumentProperties(
        key='archive_directory',
        flags=('--archive-directory',),
        type=pathlib.Path,
        description='Directory where the created archive is stored',
        argparse_kwargs={
            'required': False,
            'default': pathlib.Path('build/ios/xcarchive')
        }
    )
    IPA_DIRECTORY = cli.ArgumentProperties(
        key='ipa_directory',
        flags=('--ipa-directory',),
        type=pathlib.Path,
        description='Directory where the built ipa is stored',
        argparse_kwargs={
            'required': False,
            'default': pathlib.Path('build/ios/ipa')
        }
    )
    CUSTOM_EXPORT_OPTIONS = cli.ArgumentProperties(
        key='custom_export_options',
        flags=('--custom-export-options',),
        type=cli.CommonArgumentTypes.json_dict,
        description=(
            'Custom options for generated export options as JSON string. '
            'For example \'{"uploadBitcode": false, "uploadSymbols": false}\'.'
        ),
        argparse_kwargs={'required': False}
    )


class XcprettyArguments(cli.Argument):
    DISABLE = cli.ArgumentProperties(
        key='disable_xcpretty',
        flags=('--disable-xcpretty',),
        type=bool,
        description='Do not use XCPretty formatter to process log output',
        argparse_kwargs={'required': False, 'action': 'store_true'},
    )
    OPTIONS = cli.ArgumentProperties(
        key='xcpretty_options',
        flags=('--xcpretty-options',),
        description=(
            'Command line options for xcpretty formatter. '
            'For example "--no-color" or "--simple  --no-utf".'
        ),
        argparse_kwargs={'required': False, 'default': '--color'},
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
            self.echo(bundle_id)
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
        detector.notify()
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
                XcodeProjectArgument.PROFILE_PATHS,
                XcodeProjectArgument.EXPORT_OPTIONS_PATH,
                XcodeProjectArgument.CUSTOM_EXPORT_OPTIONS)
    def use_profiles(self,
                     xcode_project_patterns: Sequence[pathlib.Path],
                     profile_path_patterns: Sequence[pathlib.Path],
                     export_options_plist: pathlib.Path = XcodeProjectArgument.EXPORT_OPTIONS_PATH.get_default(),
                     custom_export_options: Optional[Dict] = None):
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

        available_certs = self._get_certificates_from_keychain()
        code_signing_settings_manager = CodeSigningSettingsManager(profiles, available_certs)

        try:
            for xcode_project in xcode_projects:
                code_signing_settings_manager.use_profiles(xcode_project, cli_app=self)
        except (ValueError, IOError) as error:
            raise XcodeProjectException(*error.args)

        code_signing_settings_manager.notify_profile_usage()
        export_options = code_signing_settings_manager.generate_export_options(custom_export_options)
        export_options.notify()
        export_options.save(export_options_plist)

        self.logger.info(Colors.GREEN(f'Saved export options to {export_options_plist}'))
        return export_options

    @classmethod
    def _get_certificates_from_keychain(cls) -> List[Certificate]:
        from .keychain import Keychain
        return Keychain() \
            .list_code_signing_certificates(should_print=False)

    @cli.action('build-ipa',
                XcodeProjectArgument.XCODE_PROJECT_PATH,
                XcodeProjectArgument.XCODE_WORKSPACE_PATH,
                XcodeProjectArgument.TARGET_NAME,
                XcodeProjectArgument.CONFIGURATION_NAME,
                XcodeProjectArgument.SCHEME_NAME,
                XcodeProjectArgument.ARCHIVE_DIRECTORY,
                XcodeProjectArgument.IPA_DIRECTORY,
                XcodeProjectArgument.EXPORT_OPTIONS_PATH,
                XcprettyArguments.DISABLE,
                XcprettyArguments.OPTIONS)
    def build_ipa(self,
                  xcode_project_path: Optional[pathlib.Path] = None,
                  xcode_workspace_path: Optional[pathlib.Path] = None,
                  target_name: Optional[str] = None,
                  configuration_name: Optional[str] = None,
                  scheme_name: Optional[str] = None,
                  archive_directory: pathlib.Path = XcodeProjectArgument.ARCHIVE_DIRECTORY.get_default(),
                  ipa_directory: pathlib.Path = XcodeProjectArgument.IPA_DIRECTORY.get_default(),
                  export_options_plist: pathlib.Path = XcodeProjectArgument.EXPORT_OPTIONS_PATH.get_default(),
                  disable_xcpretty: bool = False,
                  xcpretty_options: str = XcprettyArguments.OPTIONS.get_default()) -> pathlib.Path:
        """
        Build ipa by archiving the Xcode project and then exporting it
        """

        if xcode_project_path is None and xcode_workspace_path is None:
            error = 'Workspace or project argument needs to be specified'
            XcodeProjectArgument.XCODE_WORKSPACE_PATH.raise_argument_error(error)

        xcarchive: Optional[pathlib.Path] = None
        xcodebuild: Optional[Xcodebuild] = None
        export_options = ExportOptions.from_path(export_options_plist)
        try:
            xcodebuild = Xcodebuild(
                xcode_workspace=xcode_workspace_path,
                xcode_project=xcode_project_path,
                scheme_name=scheme_name,
                target_name=target_name,
                configuration_name=configuration_name,
                xcpretty=Xcpretty(xcpretty_options) if not disable_xcpretty else None,
            )

            self.logger.info(Colors.BLUE(f'Archive {(xcodebuild.workspace or xcodebuild.xcode_project).name}'))
            xcarchive = xcodebuild.archive(export_options, archive_directory, cli_app=self)
            self.logger.info(Colors.GREEN(f'Successfully created archive at {xcarchive}\n'))

            self.logger.info(Colors.BLUE(f'Export {xcarchive} to {ipa_directory}'))
            ipa = xcodebuild.export_archive(xcarchive, export_options_plist, ipa_directory, cli_app=self)
            self.logger.info(Colors.GREEN(f'Successfully exported ipa to {ipa}\n'))
        except (ValueError, IOError) as error:
            raise XcodeProjectException(*error.args)
        finally:
            if not disable_xcpretty and xcodebuild:
                self.logger.info(f'Raw xcodebuild logs stored in {xcodebuild.logs_path}')
            if xcarchive is not None:
                shutil.rmtree(xcarchive, ignore_errors=True)
        return ipa


if __name__ == '__main__':
    XcodeProject.invoke_cli()
