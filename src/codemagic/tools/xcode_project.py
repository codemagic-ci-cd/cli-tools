#!/usr/bin/env python3

from __future__ import annotations

import json
import pathlib
import re
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
from codemagic.models import CodeSignEntitlements
from codemagic.models import CodeSigningSettingsManager
from codemagic.models import ExportOptions
from codemagic.models import ProvisioningProfile
from codemagic.models import Xcode
from codemagic.models import Xcodebuild
from codemagic.models import Xcpretty
from codemagic.models.junit import TestSuitePrinter
from codemagic.models.junit import TestSuites
from codemagic.models.simulator import Runtime
from codemagic.models.simulator import Simulator
from codemagic.models.xctests import XcResultCollector
from codemagic.models.xctests import XcResultConverter

from ._xcode_project.arguments import ExportIpaArgument
from ._xcode_project.arguments import TestArgument
from ._xcode_project.arguments import TestResultArgument
from ._xcode_project.arguments import XcodeArgument
from ._xcode_project.arguments import XcodeProjectArgument
from ._xcode_project.arguments import XcprettyArgument


class XcodeProjectException(cli.CliAppException):
    pass


class XcodeProject(cli.CliApp, PathFinderMixin):
    """
    Utility to work with Xcode projects. Use it to manage iOS application
    code signing properties for builds, create IPAs and run tests
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
            raise XcodeProjectException('Unable to detect Bundle ID')
        bundle_id = bundle_ids.most_common(1)[0][0]

        self.logger.info(Colors.GREEN(f'Chose Bundle ID {bundle_id}'))
        if should_print:
            self.echo(bundle_id)
        return bundle_id

    @cli.action('use-profiles',
                XcodeProjectArgument.XCODE_PROJECT_PATTERN,
                XcodeProjectArgument.PROFILE_PATHS,
                ExportIpaArgument.EXPORT_OPTIONS_PATH,
                ExportIpaArgument.CUSTOM_EXPORT_OPTIONS,
                XcodeProjectArgument.WARN_ONLY)
    def use_profiles(self,
                     xcode_project_patterns: Sequence[pathlib.Path],
                     profile_path_patterns: Sequence[pathlib.Path],
                     export_options_plist: pathlib.Path = ExportIpaArgument.EXPORT_OPTIONS_PATH.get_default(),
                     custom_export_options: Optional[Dict] = None,
                     warn_only: bool = False):
        """
        Set up code signing settings on specified Xcode projects
        to use given provisioning profiles
        """
        from .keychain import Keychain

        self.logger.info(Colors.BLUE('Configure code signing settings'))

        profile_paths = self.find_paths(*profile_path_patterns)
        xcode_projects = self.find_paths(*xcode_project_patterns)

        try:
            profiles = [ProvisioningProfile.from_path(p) for p in profile_paths]
        except (ValueError, IOError) as error:
            raise XcodeProjectException(*error.args)

        available_certs = Keychain().list_code_signing_certificates(should_print=False)
        code_signing_settings_manager = CodeSigningSettingsManager(profiles, available_certs)

        for xcode_project in xcode_projects:
            try:
                code_signing_settings_manager.use_profiles(xcode_project)
            except (ValueError, IOError) as error:
                if warn_only:
                    self.logger.warning(Colors.YELLOW(f'Using profiles on {xcode_project} failed'))
                else:
                    raise XcodeProjectException(*error.args)

        code_signing_settings_manager.notify_profile_usage()
        export_options = code_signing_settings_manager.generate_export_options(custom_export_options)
        export_options.notify(Colors.GREEN('Generated options for exporting the project'))
        export_options.save(export_options_plist)

        self.logger.info(Colors.GREEN(f'Saved export options to {export_options_plist}'))
        return export_options

    @cli.action('clean',
                XcodeProjectArgument.XCODE_PROJECT_PATH,
                XcodeProjectArgument.XCODE_WORKSPACE_PATH,
                XcodeProjectArgument.TARGET_NAME,
                XcodeProjectArgument.CONFIGURATION_NAME,
                XcodeProjectArgument.SCHEME_NAME,
                XcprettyArgument.DISABLE,
                XcprettyArgument.OPTIONS)
    def clean(self,
              xcode_project_path: Optional[pathlib.Path] = None,
              xcode_workspace_path: Optional[pathlib.Path] = None,
              target_name: Optional[str] = None,
              configuration_name: Optional[str] = None,
              scheme_name: Optional[str] = None,
              disable_xcpretty: bool = False,
              xcpretty_options: str = XcprettyArgument.OPTIONS.get_default()):
        """
        Clean Xcode project
        """

        self._ensure_project_or_workspace(xcode_project_path, xcode_workspace_path)
        xcodebuild = self._get_xcodebuild(**locals())
        self._clean(xcodebuild)

    @cli.action('build-ipa',
                XcodeProjectArgument.XCODE_PROJECT_PATH,
                XcodeProjectArgument.XCODE_WORKSPACE_PATH,
                XcodeProjectArgument.TARGET_NAME,
                XcodeProjectArgument.CONFIGURATION_NAME,
                XcodeProjectArgument.SCHEME_NAME,
                XcodeProjectArgument.CLEAN,
                ExportIpaArgument.ARCHIVE_DIRECTORY,
                XcodeArgument.ARCHIVE_FLAGS,
                XcodeArgument.ARCHIVE_XCARGS,
                ExportIpaArgument.IPA_DIRECTORY,
                ExportIpaArgument.EXPORT_OPTIONS_PATH_EXISTING,
                XcodeArgument.EXPORT_FLAGS,
                XcodeArgument.EXPORT_XCARGS,
                ExportIpaArgument.REMOVE_XCARCHIVE,
                XcprettyArgument.DISABLE,
                XcprettyArgument.OPTIONS)
    def build_ipa(self,
                  xcode_project_path: Optional[pathlib.Path] = None,
                  xcode_workspace_path: Optional[pathlib.Path] = None,
                  target_name: Optional[str] = None,
                  configuration_name: Optional[str] = None,
                  scheme_name: Optional[str] = None,
                  clean: bool = False,
                  archive_directory: pathlib.Path = ExportIpaArgument.ARCHIVE_DIRECTORY.get_default(),
                  archive_xcargs: Optional[str] = XcodeArgument.ARCHIVE_XCARGS.get_default(),
                  archive_flags: Optional[str] = XcodeArgument.ARCHIVE_FLAGS.get_default(),
                  ipa_directory: pathlib.Path = ExportIpaArgument.IPA_DIRECTORY.get_default(),
                  export_options_plist: pathlib.Path = ExportIpaArgument.EXPORT_OPTIONS_PATH_EXISTING.get_default(),
                  export_xcargs: Optional[str] = XcodeArgument.EXPORT_XCARGS.get_default(),
                  export_flags: Optional[str] = XcodeArgument.EXPORT_FLAGS.get_default(),
                  remove_xcarchive: bool = False,
                  disable_xcpretty: bool = False,
                  xcpretty_options: str = XcprettyArgument.OPTIONS.get_default()) -> pathlib.Path:
        """
        Build ipa by archiving the Xcode project and then exporting it
        """
        self._ensure_project_or_workspace(xcode_project_path, xcode_workspace_path)

        export_options = ExportOptions.from_path(export_options_plist)
        xcodebuild = self._get_xcodebuild(**locals())
        clean and self._clean(xcodebuild)

        self.logger.info(Colors.BLUE(f'Archive {(xcodebuild.workspace or xcodebuild.xcode_project).name}'))
        try:
            xcarchive = xcodebuild.archive(
                export_options, archive_directory,
                xcargs=archive_xcargs, custom_flags=archive_flags)
        except IOError as error:
            raise XcodeProjectException(*error.args)
        self.logger.info(Colors.GREEN(f'Successfully created archive at {xcarchive}\n'))

        self._update_export_options(xcarchive, export_options_plist, export_options)

        self.logger.info(Colors.BLUE(f'Export {xcarchive} to {ipa_directory}'))
        try:
            ipa = xcodebuild.export_archive(
                xcarchive, export_options_plist, ipa_directory,
                xcargs=export_xcargs, custom_flags=export_flags)
        except IOError as error:
            raise XcodeProjectException(*error.args)
        else:
            self.logger.info(Colors.GREEN(f'Successfully exported ipa to {ipa}\n'))
        finally:
            if not disable_xcpretty:
                self.logger.info(f'Raw xcodebuild logs stored in {xcodebuild.logs_path}')
            if xcarchive is not None and remove_xcarchive:
                self.logger.info(f'Removing generated xcarchive {xcarchive.resolve()}')
                shutil.rmtree(xcarchive, ignore_errors=True)
        return ipa

    @cli.action('test-destinations',
                TestArgument.RUNTIMES,
                TestArgument.SIMULATOR_NAME,
                TestArgument.INCLUDE_UNAVAILABLE,
                XcodeProjectArgument.JSON_OUTPUT)
    def get_test_destinations(self,
                              runtimes: Optional[Sequence[Runtime]] = None,
                              simulator_name: Optional[re.Pattern] = None,
                              include_unavailable: bool = False,
                              json_output: bool = False,
                              should_print: bool = True) -> List[Simulator]:
        """
        List available destinations for test runs
        """

        try:
            all(r.validate() for r in (runtimes or []))
        except ValueError as ve:
            TestArgument.RUNTIMES.raise_argument_error(str(ve))

        self.logger.info(Colors.BLUE('List available test devices'))
        try:
            simulators = Simulator.list(runtimes, simulator_name, include_unavailable)
        except IOError as e:
            raise XcodeProjectException(str(e)) from e
        if not simulators:
            raise XcodeProjectException('No simulator runtimes are available')

        if should_print:
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
    def get_default_test_destination(self,
                                     json_output: bool = False,
                                     should_print: bool = True) -> Simulator:
        """
        Show default test destination for the chosen Xcode version
        """
        xcode = Xcode.get_selected()
        if should_print:
            msg_template = 'Show default test destination for Xcode %s (%s)'
            self.logger.info(Colors.BLUE(msg_template), xcode.version, xcode.build_version)

        try:
            simulator = Simulator.get_default()
        except ValueError as error:
            raise XcodeProjectException(str(error)) from error

        if should_print:
            if json_output:
                self.echo(json.dumps(simulator.dict(), indent=4))
            else:
                self.echo(Colors.GREEN(f'{simulator.runtime} {simulator.name}'))
        return simulator

    @cli.action('run-tests',
                XcodeProjectArgument.XCODE_PROJECT_PATH,
                XcodeProjectArgument.XCODE_WORKSPACE_PATH,
                XcodeProjectArgument.TARGET_NAME,
                XcodeProjectArgument.CONFIGURATION_NAME,
                XcodeProjectArgument.SCHEME_NAME,
                XcodeProjectArgument.CLEAN,
                TestArgument.DISABLE_CODE_COVERAGE,
                TestArgument.GRACEFUL_EXIT,
                TestArgument.MAX_CONCURRENT_DEVICES,
                TestArgument.MAX_CONCURRENT_SIMULATORS,
                TestArgument.TEST_DEVICES,
                TestArgument.TEST_ONLY,
                TestArgument.TEST_SDK,
                TestResultArgument.OUTPUT_DIRECTORY,
                TestResultArgument.OUTPUT_EXTENSION,
                XcodeArgument.TEST_FLAGS,
                XcodeArgument.TEST_XCARGS,
                XcprettyArgument.DISABLE,
                XcprettyArgument.OPTIONS)
    def run_test(self,
                 xcode_project_path: Optional[pathlib.Path] = None,
                 xcode_workspace_path: Optional[pathlib.Path] = None,
                 target_name: Optional[str] = None,
                 configuration_name: Optional[str] = None,
                 scheme_name: Optional[str] = None,
                 clean: bool = False,
                 devices: Optional[List[str]] = None,
                 disable_code_coverage: bool = False,
                 max_concurrent_devices: Optional[int] = TestArgument.MAX_CONCURRENT_DEVICES.get_default(),
                 max_concurrent_simulators: Optional[int] = TestArgument.MAX_CONCURRENT_SIMULATORS.get_default(),
                 test_only: Optional[str] = TestArgument.TEST_ONLY.get_default(),
                 test_sdk: str = TestArgument.TEST_SDK.get_default(),
                 test_xcargs: Optional[str] = XcodeArgument.TEST_XCARGS.get_default(),
                 test_flags: Optional[str] = XcodeArgument.TEST_FLAGS.get_default(),
                 disable_xcpretty: bool = False,
                 xcpretty_options: str = XcprettyArgument.OPTIONS.get_default(),
                 output_dir: pathlib.Path = TestResultArgument.OUTPUT_DIRECTORY.get_default(),
                 output_extension: str = TestResultArgument.OUTPUT_EXTENSION.get_default(),
                 graceful_exit: bool = False):
        """
        Run unit or UI tests for given Xcode project or workspace
        """
        self._ensure_project_or_workspace(xcode_project_path, xcode_workspace_path)
        simulators = self._get_test_destinations(devices)
        xcodebuild = self._get_xcodebuild(**locals())
        clean and self._clean(xcodebuild)

        self.echo(Colors.BLUE(f'Run tests for {(xcodebuild.workspace or xcodebuild.xcode_project).name}\n'))
        xcresult_collector = XcResultCollector()
        xcresult_collector.ignore_results(Xcode.DERIVED_DATA_PATH)
        try:
            xcodebuild.test(
                test_sdk,
                simulators,
                enable_code_coverage=not disable_code_coverage,
                only_testing=test_only,
                xcargs=test_xcargs,
                custom_flags=test_flags,
                max_concurrent_devices=max_concurrent_devices,
                max_concurrent_simulators=max_concurrent_simulators,
            )
        except IOError:
            testing_failed = True
            self.echo(Colors.RED('\nTest run failed\n'))
        else:
            testing_failed = False
            self.echo(Colors.GREEN('\nTest run completed successfully\n'))
        xcresult_collector.gather_results(Xcode.DERIVED_DATA_PATH)

        output_dir.mkdir(parents=True, exist_ok=True)
        self._copy_simulator_logs(simulators, output_dir)

        if not xcresult_collector.get_collected_results():
            raise XcodeProjectException('Did not find any test results')

        test_suites, xcresult = self._get_test_suites(
            xcresult_collector, show_found_result=True, save_xcresult_dir=output_dir)

        message = (
            f'Executed {test_suites.tests} tests with '
            f'{test_suites.failures} failures and '
            f'{test_suites.errors} errors in '
            f'{test_suites.time:.2f} seconds.\n'
        )
        self.echo(Colors.BLUE(message))
        TestSuitePrinter(self.echo).print_test_suites(test_suites)
        self._save_test_suite(xcresult, test_suites, output_dir, output_extension)

        if not graceful_exit:
            has_failing_tests = test_suites and (test_suites.failures or test_suites.errors)
            if testing_failed or has_failing_tests:
                raise XcodeProjectException('Tests failed')

    @cli.action('test-summary',
                TestResultArgument.XCRESULT_PATTERNS,
                TestResultArgument.XCRESULT_DIRS)
    def show_test_report_summary(
            self,
            xcresult_patterns: Optional[Sequence[pathlib.Path]] = None,
            xcresult_dirs: Sequence[pathlib.Path] = TestResultArgument.XCRESULT_DIRS.get_default()):
        """
        Show summary of Xcode Test Result
        """
        xcresult_collector = self._collect_xcresults(xcresult_patterns, xcresult_dirs)
        xcresults = xcresult_collector.get_collected_results()
        if not xcresults:
            raise XcodeProjectException('Did not find any Xcode test results for given patterns')

        test_suites, xcresult = self._get_test_suites(xcresult_collector, show_found_result=True)
        TestSuitePrinter(self.echo).print_test_suites(test_suites)

    @cli.action('junit-test-results',
                TestResultArgument.XCRESULT_PATTERNS,
                TestResultArgument.XCRESULT_DIRS,
                TestResultArgument.OUTPUT_DIRECTORY,
                TestResultArgument.OUTPUT_EXTENSION)
    def convert_xcresults_to_junit(
            self,
            xcresult_patterns: Optional[Sequence[pathlib.Path]] = None,
            xcresult_dirs: Sequence[pathlib.Path] = TestResultArgument.XCRESULT_DIRS.get_default(),
            output_dir: pathlib.Path = TestResultArgument.OUTPUT_DIRECTORY.get_default(),
            output_extension: str = TestResultArgument.OUTPUT_EXTENSION.get_default()):
        """
        Convert Xcode Test Result Bundles (*.xcresult) to JUnit XML format
        """
        xcresult_collector = self._collect_xcresults(xcresult_patterns, xcresult_dirs)
        xcresults = xcresult_collector.get_collected_results()
        if not xcresults:
            raise XcodeProjectException('Did not find any Xcode test results for given patterns')

        test_suites, xcresult = self._get_test_suites(xcresult_collector, show_found_result=True)
        self._save_test_suite(xcresult, test_suites, output_dir, output_extension)

    def _clean(self, xcodebuild: Xcodebuild):
        self.logger.info(Colors.BLUE(f'Clean {(xcodebuild.workspace or xcodebuild.xcode_project).name}'))
        try:
            xcodebuild.clean()
        except IOError as error:
            raise XcodeProjectException(*error.args)
        self.logger.info(Colors.GREEN(f'Cleaned {(xcodebuild.workspace or xcodebuild.xcode_project).name}\n'))

    def _collect_xcresults(self,
                           xcresult_patterns: Optional[Sequence[pathlib.Path]],
                           xcresult_dirs: Sequence[pathlib.Path]) -> XcResultCollector:
        glob_patterns: List[pathlib.Path] = []

        for xcresult_pattern in (xcresult_patterns or []):
            if xcresult_pattern.suffix != '.xcresult':
                raise TestResultArgument.XCRESULT_PATTERNS.raise_argument_error('Not a Xcode Test Result pattern')
            glob_patterns.append(xcresult_pattern)

        for xcresult_dir in xcresult_dirs:
            glob_patterns.append(xcresult_dir / '**/*.xcresult')

        xcresult_collector = XcResultCollector()
        for xcresult in self.find_paths(*glob_patterns):
            xcresult_collector.gather_results(xcresult)

        return xcresult_collector

    def _copy_simulator_logs(self, simulators: List[Simulator], target_directory: pathlib.Path):
        for simulator in simulators:
            simulator_description = f'{simulator.runtime}_{simulator.name}'
            log_path = simulator.get_logs_path()
            if not log_path.exists():
                self.logger.debug('No logs found for simulator %s', simulator)
                continue

            unsafe_destination_name = f'{simulator_description}{log_path.suffix}'
            destination_path = target_directory / re.sub(r'[^\w.]', '_', unsafe_destination_name)

            try:
                shutil.copy(log_path, destination_path)
            except OSError:
                self.logger.exception('Saving simulator %s logs to %s failed', simulator_description, destination_path)
            else:
                self.logger.debug('Saved simulator %s logs to %s', simulator_description, destination_path)

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
            detected_bundle_ids = detector.detect()
        except (ValueError, IOError) as error:
            raise XcodeProjectException(*error.args)

        env_var_bundle_ids, valid_bundle_ids = group(detected_bundle_ids)
        if env_var_bundle_ids:
            msg = f'Bundle IDs {", ".join(env_var_bundle_ids)} contain environment variables, exclude them.'
            self.logger.info(Colors.YELLOW(msg))
        self.logger.info(f'Detected Bundle IDs: {", ".join(valid_bundle_ids)}')
        return valid_bundle_ids

    @classmethod
    def _ensure_project_or_workspace(cls, xcode_project, xcode_workspace):
        if xcode_project is None and xcode_workspace is None:
            XcodeProjectArgument.XCODE_WORKSPACE_PATH.raise_argument_error(
                'Workspace or project argument needs to be specified')

    def _get_test_destinations(self, requested_devices: Optional[List[str]]) -> List[Simulator]:
        if not requested_devices:
            simulators = [self.get_default_test_destination(should_print=False)]
        else:
            try:
                simulators = Simulator.find_simulators(requested_devices)
            except ValueError as ve:
                raise TestArgument.TEST_DEVICES.raise_argument_error(str(ve)) from ve

        self.echo(Colors.BLUE('Running tests on simulators:'))
        for s in simulators:
            self.echo('- %s %s (%s)', s.runtime, s.name, s.udid)
        self.echo('')
        return simulators

    @classmethod
    def _get_xcodebuild(cls,
                        xcode_workspace_path: Optional[pathlib.Path] = None,
                        xcode_project_path: Optional[pathlib.Path] = None,
                        target_name: Optional[str] = None,
                        configuration_name: Optional[str] = None,
                        scheme_name: Optional[str] = None,
                        disable_xcpretty: bool = False,
                        xcpretty_options: str = '',
                        **_) -> Xcodebuild:
        try:
            return Xcodebuild(
                xcode_workspace=xcode_workspace_path,
                xcode_project=xcode_project_path,
                scheme_name=scheme_name,
                target_name=target_name,
                configuration_name=configuration_name,
                xcpretty=Xcpretty(xcpretty_options) if not disable_xcpretty else None,
            )
        except ValueError as error:
            raise XcodeProjectException(*error.args) from error

    def _get_test_suites(self,
                         xcresult_collector: XcResultCollector,
                         show_found_result: bool = False,
                         save_xcresult_dir: Optional[pathlib.Path] = None):
        if show_found_result:
            self.logger.info(Colors.GREEN('Found test results at'))
            for xcresult in xcresult_collector.get_collected_results():
                self.logger.info('- %s', xcresult)
            self.logger.info('')

        xcresult = xcresult_collector.get_merged_xcresult()
        try:
            test_suites = XcResultConverter.xcresult_to_junit(xcresult)
        finally:
            if save_xcresult_dir:
                shutil.copytree(xcresult, save_xcresult_dir / xcresult.name)
            xcresult_collector.forget_merged_result()
        return test_suites, xcresult

    def _save_test_suite(self,
                         xcresult: pathlib.Path,
                         test_suites: TestSuites,
                         output_dir: pathlib.Path,
                         output_extension: str):
        result_path = output_dir / f'{xcresult.stem}.{output_extension}'
        test_suites.save_xml(result_path)
        self.echo(Colors.GREEN('Saved JUnit XML report to %s'), result_path)

    def _update_export_options(
            self, xcarchive: pathlib.Path, export_options_path: pathlib.Path, export_options: ExportOptions):
        """
        For non-App Store exports, if the app is using either CloudKit or CloudDocuments
        extensions, then "com.apple.developer.icloud-container-environment" entitlement
        needs to be specified. Available options are Development and Production.
        Defaults to Development.
        """
        if export_options.is_app_store_export() or export_options.iCloudContainerEnvironment:
            return

        archive_entitlements = CodeSignEntitlements.from_xcarchive(xcarchive)
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
