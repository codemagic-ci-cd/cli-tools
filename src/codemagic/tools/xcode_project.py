#!/usr/bin/env python3

from __future__ import annotations

import json
import pathlib
import re
import shutil
from collections import defaultdict
from distutils.version import LooseVersion
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
from codemagic.models import CodeSignEntitlements
from codemagic.models import CodeSigningSettingsManager
from codemagic.models import ExportOptions
from codemagic.models import ProvisioningProfile
from codemagic.models import Xcode
from codemagic.models import Xcodebuild
from codemagic.models import Xcpretty
from codemagic.models.simulator import Runtime
from codemagic.models.simulator import Simulator


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
    REMOVE_XCARCHIVE = cli.ArgumentProperties(
        key='remove_xcarchive',
        flags=('--remove-xcarchive',),
        type=bool,
        description='Remove generated xcarchive container while building ipa',
        argparse_kwargs={'required': False, 'action': 'store_true'},
    )
    ARCHIVE_XCARGS = cli.ArgumentProperties(
        key='archive_xcargs',
        flags=('--archive-xcargs',),
        type=str,
        description=(
            'Pass additional arguments to xcodebuild for the archive phase. '
            'For example `COMPILER_INDEX_STORE_ENABLE=NO OTHER_LDFLAGS="-ObjC -lstdc++`.'
        ),
        argparse_kwargs={'required': False, 'default': 'COMPILER_INDEX_STORE_ENABLE=NO'},
    )
    ARCHIVE_FLAGS = cli.ArgumentProperties(
        key='archive_flags',
        flags=('--archive-flags',),
        type=str,
        description=(
            'Pass additional command line options to xcodebuild for the archive phase. '
            'For example `-derivedDataPath=$HOME/myDerivedData -quiet`.'
        ),
        argparse_kwargs={'required': False, 'default': ''},
    )
    EXPORT_XCARGS = cli.ArgumentProperties(
        key='export_xcargs',
        flags=('--export-xcargs',),
        type=str,
        description=(
            'Pass additional arguments to xcodebuild for the exportArchive phase. '
            'For example `COMPILER_INDEX_STORE_ENABLE=NO OTHER_LDFLAGS="-ObjC -lstdc++`.'
        ),
        argparse_kwargs={'required': False, 'default': 'COMPILER_INDEX_STORE_ENABLE=NO'},
    )
    EXPORT_FLAGS = cli.ArgumentProperties(
        key='export_flags',
        flags=('--export-flags',),
        type=str,
        description=(
            'Pass additional command line options to xcodebuild for the exportArchive phase. '
            'For example `-derivedDataPath=$HOME/myDerivedData -quiet`.'
        ),
        argparse_kwargs={'required': False, 'default': ''},
    )
    TEST_DEVICES = cli.ArgumentProperties(
        key='devices',
        flags=('-d', '--devices'),
        type=str,
        description=(
            'Test destination description. Either a UDID value of the device, or device name and '
            'runtime combination. If runtime is not specified, the latest available runtime for '
            'given device name will be chosen. For example '
            '"iOS 14.0 iPhone SE (2nd generation)", '
            '"iPad Pro (9.7-inch)", '
            '"tvOS 14.1 Apple TV 4K (at 1080p)", '
            '"Apple TV 4K". '
            'If no devices are specified, then the default destination will be chosen (see '
            '`xcode-project default-test-destination` for more information about default destination).'
        ),
        argparse_kwargs={
            'required': False,
            'nargs': '+',
            'metavar': 'devices',
        },
    )
    TEST_XCARGS = cli.ArgumentProperties(
        key='test_xcargs',
        flags=('--test-xcargs',),
        type=str,
        description=(
            'Pass additional arguments to xcodebuild for the test phase. '
            'For example `COMPILER_INDEX_STORE_ENABLE=NO OTHER_LDFLAGS="-ObjC -lstdc++`.'
        ),
        argparse_kwargs={'required': False, 'default': ''},
    )
    TEST_SDK = cli.ArgumentProperties(
        key='test_sdk',
        flags=('--sdk',),
        type=str,
        description='Name of the SDK that should be used for building the application for testing.',
        argparse_kwargs={'required': False, 'default': 'iphonesimulator'},
    )
    TEST_FLAGS = cli.ArgumentProperties(
        key='test_flags',
        flags=('--test-flags',),
        type=str,
        description=(
            'Pass additional command line options to xcodebuild for the test phase. '
            'For example `-derivedDataPath=$HOME/myDerivedData -quiet`.'
        ),
        argparse_kwargs={'required': False, 'default': ''},
    )
    RUNTIMES = cli.ArgumentProperties(
        key='runtimes',
        flags=('--runtimes',),
        type=Runtime,
        description='Runtime name. For example "iOS 14.1", "tvOS 14", "watchOS 7".',
        argparse_kwargs={
            'required': False,
            'nargs': '+',
            'metavar': 'runtime',
        },
    )
    JSON_OUTPUT = cli.ArgumentProperties(
        key='json_output',
        flags=('--json',),
        type=bool,
        description='Whether to show the resource in JSON format',
        argparse_kwargs={'required': False, 'action': 'store_true'},
    )
    INCLUDE_UNAVAILABLE = cli.ArgumentProperties(
        key='include_unavailable',
        flags=('--unavailable', '--include-unavailable'),
        type=bool,
        description='Whether to include unavailable devices in output',
        argparse_kwargs={'required': False, 'action': 'store_true'},
    )
    SIMULATOR_NAME = cli.ArgumentProperties(
        key='simulator_name',
        flags=('--name',),
        type=re.compile,
        description='Regex pattern to filter simulators by name',
        argparse_kwargs={'required': False, 'default': None},
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
        export_options.notify(Colors.GREEN('Generated options for exporting IPA'))
        export_options.save(export_options_plist)

        self.logger.info(Colors.GREEN(f'Saved export options to {export_options_plist}'))
        return export_options

    @classmethod
    def _get_certificates_from_keychain(cls) -> List[Certificate]:
        from .keychain import Keychain
        return Keychain() \
            .list_code_signing_certificates(should_print=False)

    @cli.action('run-tests',
                XcodeProjectArgument.XCODE_PROJECT_PATH,
                XcodeProjectArgument.XCODE_WORKSPACE_PATH,
                XcodeProjectArgument.TARGET_NAME,
                XcodeProjectArgument.CONFIGURATION_NAME,
                XcodeProjectArgument.SCHEME_NAME,
                XcodeProjectArgument.TEST_DEVICES,
                XcodeProjectArgument.TEST_SDK,
                XcodeProjectArgument.TEST_FLAGS,
                XcodeProjectArgument.TEST_XCARGS,
                XcprettyArguments.DISABLE,
                XcprettyArguments.OPTIONS)
    def run_test(self,
                 xcode_project_path: Optional[pathlib.Path] = None,
                 xcode_workspace_path: Optional[pathlib.Path] = None,
                 target_name: Optional[str] = None,
                 configuration_name: Optional[str] = None,
                 scheme_name: Optional[str] = None,
                 devices: Optional[List[str]] = None,
                 test_sdk: str = XcodeProjectArgument.TEST_SDK.get_default(),
                 test_xcargs: Optional[str] = XcodeProjectArgument.TEST_XCARGS.get_default(),
                 test_flags: Optional[str] = XcodeProjectArgument.TEST_FLAGS.get_default(),
                 disable_xcpretty: bool = False,
                 xcpretty_options: str = XcprettyArguments.OPTIONS.get_default()):
        """
        Run unit or UI tests for given Xcode project or workspace
        """

        if xcode_project_path is None and xcode_workspace_path is None:
            error = 'Workspace or project argument needs to be specified'
            XcodeProjectArgument.XCODE_WORKSPACE_PATH.raise_argument_error(error)

        if not devices:
            simulators = [self.get_default_test_destination()]
        else:
            try:
                simulators = Simulator.find_simulators(devices, cli_app=self)
            except ValueError as ve:
                raise XcodeProjectArgument.TEST_DEVICES.raise_argument_error(str(ve)) from ve

        self.logger.info(Colors.GREEN('Running tests on simulators:'))
        for s in simulators:
            self.logger.info('%s (%s)', s.name, s.udid)

        try:
            xcodebuild = Xcodebuild(
                xcode_workspace=xcode_workspace_path,
                xcode_project=xcode_project_path,
                scheme_name=scheme_name,
                target_name=target_name,
                configuration_name=configuration_name,
                xcpretty=Xcpretty(xcpretty_options) if not disable_xcpretty else None,
            )

            self.logger.info(Colors.BLUE(f'Run tests for {(xcodebuild.workspace or xcodebuild.xcode_project).name}'))
            xcodebuild.test(
                test_sdk,
                simulators,
                xcargs=test_xcargs,
                custom_flags=test_flags,
                cli_app=self)
            self.logger.info(Colors.GREEN(f'Test run completed successfully\n'))
        except (ValueError, IOError) as error:
            raise XcodeProjectException(*error.args)

    @cli.action('build-ipa',
                XcodeProjectArgument.XCODE_PROJECT_PATH,
                XcodeProjectArgument.XCODE_WORKSPACE_PATH,
                XcodeProjectArgument.TARGET_NAME,
                XcodeProjectArgument.CONFIGURATION_NAME,
                XcodeProjectArgument.SCHEME_NAME,
                XcodeProjectArgument.ARCHIVE_DIRECTORY,
                XcodeProjectArgument.ARCHIVE_FLAGS,
                XcodeProjectArgument.ARCHIVE_XCARGS,
                XcodeProjectArgument.IPA_DIRECTORY,
                XcodeProjectArgument.EXPORT_OPTIONS_PATH,
                XcodeProjectArgument.EXPORT_FLAGS,
                XcodeProjectArgument.EXPORT_XCARGS,
                XcodeProjectArgument.REMOVE_XCARCHIVE,
                XcprettyArguments.DISABLE,
                XcprettyArguments.OPTIONS)
    def build_ipa(self,
                  xcode_project_path: Optional[pathlib.Path] = None,
                  xcode_workspace_path: Optional[pathlib.Path] = None,
                  target_name: Optional[str] = None,
                  configuration_name: Optional[str] = None,
                  scheme_name: Optional[str] = None,
                  archive_directory: pathlib.Path = XcodeProjectArgument.ARCHIVE_DIRECTORY.get_default(),
                  archive_xcargs: Optional[str] = XcodeProjectArgument.ARCHIVE_XCARGS.get_default(),
                  archive_flags: Optional[str] = XcodeProjectArgument.ARCHIVE_FLAGS.get_default(),
                  ipa_directory: pathlib.Path = XcodeProjectArgument.IPA_DIRECTORY.get_default(),
                  export_options_plist: pathlib.Path = XcodeProjectArgument.EXPORT_OPTIONS_PATH.get_default(),
                  export_xcargs: Optional[str] = XcodeProjectArgument.EXPORT_XCARGS.get_default(),
                  export_flags: Optional[str] = XcodeProjectArgument.EXPORT_FLAGS.get_default(),
                  remove_xcarchive: bool = False,
                  disable_xcpretty: bool = False,
                  xcpretty_options: str = XcprettyArguments.OPTIONS.get_default()) -> pathlib.Path:
        """
        Build ipa by archiving the Xcode project and then exporting it
        """

        if xcode_project_path is None and xcode_workspace_path is None:
            error = 'Workspace or project argument needs to be specified'
            XcodeProjectArgument.XCODE_WORKSPACE_PATH.raise_argument_error(error)
        if not export_options_plist.is_file():
            error = f'Path "{export_options_plist}" does not exist'
            XcodeProjectArgument.EXPORT_OPTIONS_PATH.raise_argument_error(error)

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
            xcarchive = xcodebuild.archive(
                export_options,
                archive_directory,
                xcargs=archive_xcargs,
                custom_flags=archive_flags,
                cli_app=self)
            self.logger.info(Colors.GREEN(f'Successfully created archive at {xcarchive}\n'))

            self._update_export_options(xcarchive, export_options_plist, export_options)

            self.logger.info(Colors.BLUE(f'Export {xcarchive} to {ipa_directory}'))
            ipa = xcodebuild.export_archive(
                xcarchive,
                export_options_plist,
                ipa_directory,
                xcargs=export_xcargs,
                custom_flags=export_flags,
                cli_app=self)
            self.logger.info(Colors.GREEN(f'Successfully exported ipa to {ipa}\n'))
        except (ValueError, IOError) as error:
            raise XcodeProjectException(*error.args)
        finally:
            if not disable_xcpretty and xcodebuild:
                self.logger.info(f'Raw xcodebuild logs stored in {xcodebuild.logs_path}')
            if xcarchive is not None and remove_xcarchive:
                self.logger.info(f'Removing generated xcarchive {xcarchive.resolve()}')
                shutil.rmtree(xcarchive, ignore_errors=True)
        return ipa

    @cli.action('list-test-destinations',
                XcodeProjectArgument.RUNTIMES,
                XcodeProjectArgument.SIMULATOR_NAME,
                XcodeProjectArgument.INCLUDE_UNAVAILABLE,
                XcodeProjectArgument.JSON_OUTPUT)
    def list_test_destinations(self,
                               runtimes: Optional[Sequence[Runtime]] = None,
                               simulator_name: Optional[re.Pattern] = None,
                               include_unavailable: bool = False,
                               json_output: bool = False) -> List[Simulator]:
        """
        List available destinations for test runs
        """
        self.logger.info(f'List available test devices')
        try:
            simulators = Simulator.list(runtimes, simulator_name, include_unavailable, cli_app=self)
        except IOError as e:
            raise XcodeProjectException(str(e)) from e
        if not simulators:
            raise XcodeProjectException('No simulator runtimes are available')

        if json_output:
            self.echo(json.dumps([s.dict() for s in simulators], indent=4))
        else:
            runtime_simulators = defaultdict(list)
            for s in simulators:
                runtime_simulators[s.runtime].append(s)
            for runtime in sorted(runtime_simulators.keys()):
                self.echo(Colors.GREEN('Runtime: %s'), runtime)
                for simulator in runtime_simulators[runtime]:
                    self.echo(f'- {simulator.name}')
        return simulators

    @cli.action('default-test-destination', XcodeProjectArgument.JSON_OUTPUT)
    def get_default_test_destination(self, json_output: bool = False) -> Simulator:
        """
        Show default test destination for the chosen Xcode version
        """
        xcode = Xcode.get_selected(cli_app=self)
        self.logger.info('Show default test destination for Xcode %s (%s)', xcode.version, xcode.build_version)
        try:
            simulator = Simulator.get_default(cli_app=self)
        except ValueError as ve:
            raise XcodeProjectException(str(ve)) from ve

        if json_output:
            self.echo(json.dumps(simulator.dict(), indent=4))
        else:
            self.echo(Colors.GREEN(f'{simulator.runtime} {simulator.name}'))
        return simulator

    def _update_export_options(
            self, xcarchive: pathlib.Path, export_options_path: pathlib.Path, export_options: ExportOptions):
        # For non-App Store exports, if the app is using either CloudKit or CloudDocuments
        # extensions, then "com.apple.developer.icloud-container-environment" entitlement
        # needs to be specified. Available options are Development and Production.
        # Defaults to Development.

        if export_options.is_app_store_export() or export_options.iCloudContainerEnvironment:
            return

        archive_entitlements = CodeSignEntitlements.from_xcarchive(xcarchive, cli_app=self)
        icloud_services = archive_entitlements.get_icloud_services()
        if not {'CloudKit', 'CloudDocuments'}.intersection(icloud_services):
            return

        if 'Production' in archive_entitlements.get_icloud_container_environments():
            icloud_container_environment = 'Production'
        else:
            icloud_container_environment = 'Development'

        self.echo('App is using iCloud services that require iCloudContainerEnvironment export option')
        self.echo('Set iCloudContainerEnvironment export option to %s', icloud_container_environment)
        export_options.set_value('iCloudContainerEnvironment', icloud_container_environment)
        export_options.notify(Colors.GREEN('\nUsing options for exporting IPA'))
        export_options.save(export_options_path)


if __name__ == '__main__':
    XcodeProject.invoke_cli()
