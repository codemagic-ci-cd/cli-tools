import pathlib
import re

from codemagic import cli
from codemagic.models import ProvisioningProfile
from codemagic.models.simulator import Runtime


class XcodeProjectArgument(cli.Argument):
    CLEAN = cli.ArgumentProperties(
        key='clean',
        flags=('--clean',),
        type=bool,
        description='Whether to clean the project before building it',
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
        type=cli.CommonArgumentTypes.json_dict,
        description=(
            'Custom options for generated export options as JSON string. '
            'For example \'{"uploadBitcode": false, "uploadSymbols": false}\'.'
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
    EXPORT_OPTIONS_PATH_EXISTING = cli.ArgumentProperties(
        key='export_options_plist',
        flags=('--export-options-plist',),
        type=cli.CommonArgumentTypes.existing_path,
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
            'If no devices are specified, then the default destination will be chosen (see '
            '`xcode-project default-test-destination` for more information about default destination).'
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
        type=cli.CommonArgumentTypes.existing_dir,
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
