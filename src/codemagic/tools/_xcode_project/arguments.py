import json
import pathlib
import re
from argparse import ArgumentTypeError
from dataclasses import fields
from typing import Dict

from codemagic import cli
from codemagic.cli import Colors
from codemagic.models import ArchiveMethod
from codemagic.models import ExportOptions
from codemagic.models import ProvisioningProfile
from codemagic.models.simulator import Runtime


class CodeSigningSetupVerboseLogging(cli.TypedCliArgument[bool]):
    argument_type = bool
    environment_variable_key = 'XCODE_PROJECT_CODE_SIGNING_SETUP_VERBOSE_LOGGING'


class NoShowBuildSettings(cli.TypedCliArgument[bool]):
    argument_type = bool
    environment_variable_key = 'XCODE_PROJECT_NO_SHOW_BUILD_SETTINGS'


class CustomExportOptions(cli.EnvironmentArgumentValue[dict]):
    argument_type = dict
    environment_variable_key = 'XCODE_PROJECT_CUSTOM_EXPORT_OPTIONS'
    example_value = json.dumps({
        'uploadBitcode': False,
        'uploadSymbols': False,
    })

    @classmethod
    def _apply_type(cls, non_typed_value: str) -> Dict:
        try:
            given_custom_export_options = json.loads(non_typed_value)
            if not isinstance(given_custom_export_options, dict):
                raise ValueError('Not a dict')
        except ValueError:
            raise ArgumentTypeError(f'Provided value {non_typed_value!r} is not a valid JSON encoded object')

        allowed_fields = {field.name for field in fields(ExportOptions)}
        invalid_keys = given_custom_export_options.keys() - allowed_fields
        if invalid_keys:
            keys = ', '.join(map(str, invalid_keys))
            raise ArgumentTypeError(f'Unknown export option(s): {keys}')

        return given_custom_export_options


class XcodeProjectArgument(cli.Argument):
    CLEAN = cli.ArgumentProperties(
        key='clean',
        flags=('--clean',),
        type=bool,
        description='Whether to clean the project before building it',
        argparse_kwargs={'required': False, 'action': 'store_true'},
    )
    DISABLE_SHOW_BUILD_SETTINGS = cli.ArgumentProperties(
        key='disable_show_build_settings',
        flags=('--no-show-build-settings',),
        type=NoShowBuildSettings,
        description='Do not show build settings for the project before building it',
        argparse_kwargs={'required': False, 'action': 'store_true'},
    )
    JSON_OUTPUT = cli.ArgumentProperties(
        key='json_output',
        flags=('--json',),
        type=bool,
        description='Whether to show the resource in JSON format',
        argparse_kwargs={'required': False, 'action': 'store_true'},
    )
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
            'metavar': 'project-path',
        },
    )
    XCODE_PROJECT_PATH = cli.ArgumentProperties(
        key='xcode_project_path',
        flags=('--project',),
        type=cli.CommonArgumentTypes.existing_path,
        description='Path to Xcode project (*.xcodeproj)',
        argparse_kwargs={'required': False},
    )
    XCODE_WORKSPACE_PATH = cli.ArgumentProperties(
        key='xcode_workspace_path',
        flags=('--workspace',),
        type=cli.CommonArgumentTypes.existing_path,
        description='Path to Xcode workspace (*.xcworkspace)',
        argparse_kwargs={'required': False},
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
            'default': (
                ProvisioningProfile.DEFAULT_LOCATION / '*.mobileprovision',
                ProvisioningProfile.DEFAULT_LOCATION / '*.provisionprofile',
            ),
        },
    )
    USE_PROFILE_ARCHIVE_METHOD = cli.ArgumentProperties(
        key='archive_method',
        flags=('--archive-method',),
        type=ArchiveMethod,
        description=(
            'Use only the profiles that are eligible for given archive method '
            'for code signing setup. If not specified, all found profiles will be used.'
        ),
        argparse_kwargs={'required': False, 'choices': list(ArchiveMethod)},
    )
    WARN_ONLY = cli.ArgumentProperties(
        key='warn_only',
        flags=('--warn-only',),
        type=bool,
        description=(
            'Show warning when profiles cannot be applied to any of the Xcode projects '
            'instead of fully failing the action'
        ),
        argparse_kwargs={'required': False, 'action': 'store_true'},
    )
    CODE_SIGNING_SETUP_VERBOSE_LOGGING = cli.ArgumentProperties(
        key='code_signing_setup_verbose_logging',
        flags=('--code-signing-setup-verbose-logging',),
        type=CodeSigningSetupVerboseLogging,
        description='Show verbose log output when configuring code signing settings for Xcode project.',
        argparse_kwargs={
            'required': False,
            'action': 'store_true',
        },
    )
    IPA_PATH = cli.ArgumentProperties(
        key='ipa_path',
        type=cli.CommonArgumentTypes.existing_path,
        description='Path to iOS App Store Package file (.ipa)',
    )
    PKG_PATH = cli.ArgumentProperties(
        key='pkg_path',
        type=cli.CommonArgumentTypes.existing_path,
        description='Path to MacOs Application Package file (.pkg)',
    )


class ExportIpaArgument(cli.Argument):
    ARCHIVE_DIRECTORY = cli.ArgumentProperties(
        key='archive_directory',
        flags=('--archive-directory',),
        type=pathlib.Path,
        description='Directory where the created archive is stored',
        argparse_kwargs={
            'required': False,
            'default': pathlib.Path('build/ios/xcarchive'),
        },
    )
    CUSTOM_EXPORT_OPTIONS = cli.ArgumentProperties(
        key='custom_export_options',
        flags=('--custom-export-options',),
        type=CustomExportOptions,
        description=(
            'Custom options for generated export options as JSON string. '
            f'For example, "{Colors.WHITE(CustomExportOptions.example_value)}".'
        ),
        argparse_kwargs={'required': False},
    )
    EXPORT_OPTIONS_PATH = cli.ArgumentProperties(
        key='export_options_plist',
        flags=('--export-options-plist',),
        type=pathlib.Path,
        description='Path to the generated export options plist',
        argparse_kwargs={
            'required': False,
            'default': pathlib.Path('~/export_options.plist').expanduser(),
        },
    )
    IPA_DIRECTORY = cli.ArgumentProperties(
        key='ipa_directory',
        flags=('--ipa-directory',),
        type=pathlib.Path,
        description='Directory where the built ipa is stored',
        argparse_kwargs={
            'required': False,
            'default': pathlib.Path('build/ios/ipa'),
        },
    )
    REMOVE_XCARCHIVE = cli.ArgumentProperties(
        key='remove_xcarchive',
        flags=('--remove-xcarchive',),
        type=bool,
        description='Remove generated xcarchive container while building ipa',
        argparse_kwargs={'required': False, 'action': 'store_true'},
    )


class TestArgument(cli.Argument):
    DISABLE_CODE_COVERAGE = cli.ArgumentProperties(
        key='disable_code_coverage',
        flags=('--disable-coverage',),
        type=bool,
        description='Turn code coverage off when testing',
        argparse_kwargs={'required': False, 'action': 'store_true'},
    )
    GRACEFUL_EXIT = cli.ArgumentProperties(
        key='graceful_exit',
        flags=('--graceful-exit',),
        type=bool,
        description=(
            'In case of failed tests or unsuccessful test run exit '
            'the program with status code 0'
        ),
        argparse_kwargs={'required': False, 'action': 'store_true'},
    )
    INCLUDE_UNAVAILABLE = cli.ArgumentProperties(
        key='include_unavailable',
        flags=('-u', '--include-unavailable'),
        type=bool,
        description='Whether to include unavailable devices in output',
        argparse_kwargs={'required': False, 'action': 'store_true'},
    )
    MAX_CONCURRENT_DEVICES = cli.ArgumentProperties(
        key='max_concurrent_devices',
        flags=('--max-concurrent-devices',),
        type=int,
        description='The maximum number of device destinations to test on concurrently.',
        argparse_kwargs={'required': False, 'default': None},
    )
    MAX_CONCURRENT_SIMULATORS = cli.ArgumentProperties(
        key='max_concurrent_simulators',
        flags=('--max-concurrent-simulators',),
        type=int,
        description='The maximum number of simulator destinations to test on concurrently.',
        argparse_kwargs={'required': False, 'default': None},
    )
    RUNTIMES = cli.ArgumentProperties(
        key='runtimes',
        flags=('-r', '--runtime'),
        type=Runtime,
        description='Runtime name. For example "iOS 14.1", "tvOS 14", "watchOS 7".',
        argparse_kwargs={
            'required': False,
            'nargs': '+',
            'metavar': 'runtime',
        },
    )
    SIMULATOR_NAME = cli.ArgumentProperties(
        key='simulator_name',
        flags=('-n', '--name'),
        type=re.compile,
        description='Regex pattern to filter simulators by name. For example "iPad Air 2", "iPhone 11".',
        argparse_kwargs={'required': False, 'default': None},
    )
    TEST_DEVICES = cli.ArgumentProperties(
        key='devices',
        flags=('-d', '--device'),
        type=str,
        description=(
            'Test destination description. Either a UDID value of the device, or device name and '
            'runtime combination. If runtime is not specified, the latest available runtime for '
            'given device name will be chosen. For example '
            '"iOS 14.0 iPhone SE (2nd generation)", '
            '"iPad Pro (9.7-inch)", '
            '"tvOS 14.1 Apple TV 4K (at 1080p)", '
            '"Apple TV 4K". '
            'Default test destination will be chosen if no devices are specified and test SDK is not '
            'targeting macOS. For macOS tests no destination are specified. '
            '(See `xcode-project default-test-destination` for more information about default destination).'
        ),
        argparse_kwargs={
            'required': False,
            'nargs': '+',
            'metavar': 'device_description',
        },
    )
    TEST_ONLY = cli.ArgumentProperties(
        key='test_only',
        flags=('--test-only',),
        type=str,
        description='Limit test run to execute only specified tests, and exclude all other tests',
        argparse_kwargs={'required': False, 'default': None},
    )
    TEST_SDK = cli.ArgumentProperties(
        key='test_sdk',
        flags=('--sdk',),
        type=str,
        description='Name of the SDK that should be used for building the application for testing.',
        argparse_kwargs={'required': False, 'default': 'iphonesimulator'},
    )


class TestResultArgument(cli.Argument):
    XCRESULT_PATTERNS = cli.ArgumentProperties(
        key='xcresult_patterns',
        flags=('-p', '--xcresult'),
        type=cli.CommonArgumentTypes.existing_dir,
        description=(
            'Path to Xcode Test result (*.xcresult) to be be converted. '
            'Can be either a path literal, or a glob pattern to match xcresults '
            'in working directory. '
            'If no search paths are provided, look for *.xcresults from current directory.'
        ),
        argparse_kwargs={
            'required': False,
            'default': None,
            'nargs': '+',
            'metavar': 'xcresult-pattern',
        },
    )
    XCRESULT_DIRS = cli.ArgumentProperties(
        key='xcresult_dirs',
        flags=('-d', '--dir'),
        type=cli.CommonArgumentTypes.existing_dir,
        description=(
            'Directory where Xcode Test results (*.xcresult) should be converted. '
            'If no search paths are provided, look for *.xcresults from current directory.'
        ),
        argparse_kwargs={
            'required': False,
            'default': [],
            'nargs': '+',
            'metavar': 'xcresult-dir',
        },
    )
    OUTPUT_DIRECTORY = cli.ArgumentProperties(
        key='output_dir',
        flags=('-o', '--output-dir'),
        type=cli.CommonArgumentTypes.maybe_dir,
        description='Directory where the Junit XML results will be saved.',
        argparse_kwargs={
            'required': False,
            'default': pathlib.Path('build/ios/test'),
        },
    )
    OUTPUT_EXTENSION = cli.ArgumentProperties(
        key='output_extension',
        flags=('-e', '--output-extension'),
        type=str,
        description='Extension for the created Junit XML file. For example `xml` or `junit`.',
        argparse_kwargs={
            'required': False,
            'default': 'xml',
        },
    )


class XcprettyArgument(cli.Argument):
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


class XcodeArgument(cli.Argument):
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
