import json
import pathlib
import re
from argparse import ArgumentTypeError
from collections import Counter
from dataclasses import dataclass
from typing import List
from typing import Optional

from codemagic import cli
from codemagic.apple.app_store_connect import AppStoreConnectApiClient
from codemagic.apple.app_store_connect import IssuerId
from codemagic.apple.app_store_connect import KeyIdentifier
from codemagic.apple.resources import AppStoreState
from codemagic.apple.resources import BuildProcessingState
from codemagic.apple.resources import BundleIdPlatform
from codemagic.apple.resources import CertificateType
from codemagic.apple.resources import DeviceStatus
from codemagic.apple.resources import Locale
from codemagic.apple.resources import Platform
from codemagic.apple.resources import ProfileState
from codemagic.apple.resources import ProfileType
from codemagic.apple.resources import ResourceId
from codemagic.cli import Colors
from codemagic.models import Certificate
from codemagic.models import ProvisioningProfile


@dataclass
class BetaBuildInfo:
    whats_new: str
    locale: Optional[Locale]


class Types:
    class IssuerIdArgument(cli.EnvironmentArgumentValue[IssuerId]):
        argument_type = IssuerId
        environment_variable_key = 'APP_STORE_CONNECT_ISSUER_ID'

    class KeyIdentifierArgument(cli.EnvironmentArgumentValue[KeyIdentifier]):
        argument_type = KeyIdentifier
        environment_variable_key = 'APP_STORE_CONNECT_KEY_IDENTIFIER'

    class PrivateKeyArgument(cli.EnvironmentArgumentValue[str]):
        PRIVATE_KEY_LOCATIONS = (
            pathlib.Path('./private_keys'),
            pathlib.Path('~/private_keys'),
            pathlib.Path('~/.private_keys'),
            pathlib.Path('~/.appstoreconnect/private_keys'),
        )
        environment_variable_key = 'APP_STORE_CONNECT_PRIVATE_KEY'

        @classmethod
        def _is_valid(cls, value: str) -> bool:
            return value.startswith('-----BEGIN ')

    class CertificateKeyArgument(PrivateKeyArgument):
        environment_variable_key = 'CERTIFICATE_PRIVATE_KEY'

    class CertificateKeyPasswordArgument(cli.EnvironmentArgumentValue):
        environment_variable_key = 'CERTIFICATE_PRIVATE_KEY_PASSWORD'

    class AppSpecificPassword(cli.EnvironmentArgumentValue):
        environment_variable_key = 'APP_SPECIFIC_PASSWORD'

        @classmethod
        def _is_valid(cls, value: str) -> bool:
            return bool(re.match(r'^([a-z]{4}-){3}[a-z]{4}$', value))

    class WhatsNewArgument(cli.EnvironmentArgumentValue[str]):
        environment_variable_key = 'APP_STORE_CONNECT_WHATS_NEW'

    class AppStoreConnectSkipPackageValidation(cli.TypedCliArgument[bool]):
        argument_type = bool
        environment_variable_key = 'APP_STORE_CONNECT_SKIP_PACKAGE_VALIDATION'

    class MaxBuildProcessingWait(cli.TypedCliArgument[int]):
        argument_type = int
        environment_variable_key = 'APP_STORE_CONNECT_MAX_BUILD_PROCESSING_WAIT'
        default_value = 20

    class BetaBuildLocalizations(cli.EnvironmentArgumentValue[List[BetaBuildInfo]]):
        argument_type = List[BetaBuildInfo]
        environment_variable_key = 'APP_STORE_CONNECT_BETA_BUILD_LOCALIZATIONS'
        example_value = json.dumps([{'locale': 'en-US', 'whats_new': "What's new in English"}])

        @classmethod
        def _apply_type(cls, non_typed_value: str) -> List[BetaBuildInfo]:
            try:
                given_beta_build_localizations = json.loads(non_typed_value)
                assert isinstance(given_beta_build_localizations, list)
            except (ValueError, AssertionError):
                raise ArgumentTypeError(f'Provided value {non_typed_value!r} is not a valid JSON encoded list')

            beta_build_infos: List[BetaBuildInfo] = []
            error_prefix = 'Invalid beta build localization'
            for i, bbl in enumerate(given_beta_build_localizations):
                try:
                    whats_new: str = bbl['whats_new']
                    locale = Locale(bbl['locale'])
                except TypeError:  # Given beta build localization is not a dictionary
                    raise ArgumentTypeError(f'{error_prefix} value {bbl!r} on index {i}')
                except ValueError as ve:  # Invalid locale
                    raise ArgumentTypeError(f'{error_prefix} on index {i}, {ve} in {bbl!r}')
                except KeyError as ke:  # Required key is missing from input
                    raise ArgumentTypeError(f'{error_prefix} on index {i}, missing {ke.args[0]} in {bbl!r}')
                beta_build_infos.append(BetaBuildInfo(whats_new=whats_new, locale=locale))

            locales = Counter(info.locale for info in beta_build_infos)
            duplicate_locales = {locale.value for locale, uses in locales.items() if locale and uses > 1}
            if duplicate_locales:
                raise ArgumentTypeError((
                    f'Ambiguous definitions for locale(s) {", ".join(duplicate_locales)}. '
                    'Please define beta build localization for each locale exactly once.'
                ))

            return beta_build_infos


_API_DOCS_REFERENCE = f'Learn more at {AppStoreConnectApiClient.API_KEYS_DOCS_URL}.'


class AppArgument(cli.Argument):
    APPLICATION_ID_RESOURCE_ID = cli.ArgumentProperties(
        key='application_id',
        type=ResourceId,
        description='Application Apple ID. An automatically generated ID assigned to your app',
    )
    APPLICATION_ID_RESOURCE_ID_OPTIONAL = cli.ArgumentProperties(
        key='application_id',
        flags=('--app-id', '--application-id'),
        type=ResourceId,
        description='Application Apple ID. An automatically generated ID assigned to your app',
        argparse_kwargs={'required': False},
    )
    APPLICATION_NAME = cli.ArgumentProperties(
        key='application_name',
        flags=('--app-name', '--application-name'),
        description='The name of your app as it will appear in the App Store',
        argparse_kwargs={'required': False},
    )
    APPLICATION_SKU = cli.ArgumentProperties(
        key='application_sku',
        flags=('--app-sku', '--application-sku'),
        description='A unique ID for your app that is not visible on the App Store.',
        argparse_kwargs={'required': False},
    )


class AppStoreConnectArgument(cli.Argument):
    LOG_REQUESTS = cli.ArgumentProperties(
        key='log_requests',
        flags=('--log-api-calls',),
        type=bool,
        description='Turn on logging for App Store Connect API HTTP requests',
        argparse_kwargs={'required': False, 'action': 'store_true'},
    )
    JSON_OUTPUT = cli.ArgumentProperties(
        key='json_output',
        flags=('--json',),
        type=bool,
        description='Whether to show the resource in JSON format',
        argparse_kwargs={'required': False, 'action': 'store_true'},
    )
    ISSUER_ID = cli.ArgumentProperties(
        key='issuer_id',
        flags=('--issuer-id',),
        type=Types.IssuerIdArgument,
        description=(
            f'App Store Connect API Key Issuer ID. Identifies the issuer '
            f'who created the authentication token. {_API_DOCS_REFERENCE}'
        ),
        argparse_kwargs={'required': False},
    )
    KEY_IDENTIFIER = cli.ArgumentProperties(
        key='key_identifier',
        flags=('--key-id',),
        type=Types.KeyIdentifierArgument,
        description=f'App Store Connect API Key ID. {_API_DOCS_REFERENCE}',
        argparse_kwargs={'required': False},
    )
    PRIVATE_KEY = cli.ArgumentProperties(
        key='private_key',
        flags=('--private-key',),
        type=Types.PrivateKeyArgument,
        description=(
            f'App Store Connect API private key used for JWT authentication to communicate with Apple services. '
            f'{_API_DOCS_REFERENCE} '
            f'If not provided, the key will be searched from the following directories '
            f'in sequence for a private key file with the name "AuthKey_<key_identifier>.p8": '
            f'{", ".join(map(str, Types.PrivateKeyArgument.PRIVATE_KEY_LOCATIONS))}, where '
            f'<key_identifier> is the value of {Colors.BRIGHT_BLUE("--key-id")}'
        ),
        argparse_kwargs={'required': False},
    )
    CERTIFICATES_DIRECTORY = cli.ArgumentProperties(
        key='certificates_directory',
        flags=('--certificates-dir',),
        type=pathlib.Path,
        description='Directory where the code signing certificates will be saved',
        argparse_kwargs={'required': False, 'default': Certificate.DEFAULT_LOCATION},
    )
    PROFILES_DIRECTORY = cli.ArgumentProperties(
        key='profiles_directory',
        flags=('--profiles-dir',),
        type=pathlib.Path,
        description='Directory where the provisioning profiles will be saved',
        argparse_kwargs={'required': False, 'default': ProvisioningProfile.DEFAULT_LOCATION},
    )


class AppStoreVersionArgument(cli.Argument):
    APP_STORE_STATE = cli.ArgumentProperties(
        key='app_store_state',
        flags=('--state', '--app-store-version-state'),
        type=AppStoreState,
        description='State of App Store Version',
        argparse_kwargs={
            'required': False,
            'choices': list(AppStoreState),
        },
    )
    APP_STORE_VERSION_ID = cli.ArgumentProperties(
        key='app_store_version_id',
        type=ResourceId,
        description='UUID value of the App Store Version',
    )
    APP_STORE_VERSION_ID_OPTIONAL = cli.ArgumentProperties(
        key='app_store_version_id',
        flags=('--version-id', '--app-store-version-id'),
        type=ResourceId,
        description='UUID value of the App Store Version',
        argparse_kwargs={'required': False},
    )
    APP_STORE_VERSION_SUBMISSION_ID = cli.ArgumentProperties(
        key='app_store_version_submission_id',
        type=ResourceId,
        description='UUID value of the App Store Version Submission',
    )
    PLATFORM = cli.ArgumentProperties(
        key='platform',
        flags=('--platform', '--app-store-version-platform'),
        type=Platform,
        description='App Store Version platform',
        argparse_kwargs={
            'required': False,
            'choices': list(Platform),
        },
    )
    VERSION_STRING = cli.ArgumentProperties(
        key='version_string',
        flags=('--version-string', '--app-store-version'),
        description=(
            'Version of the build published to App Store '
            'that identifies an iteration of the bundle. '
            'The string can only contain one to three groups of numeric characters (0-9) '
            'separated by period in the format [Major].[Minor].[Patch]. '
            'For example `3.2.46`'
        ),
        argparse_kwargs={'required': False},
    )


class PublishArgument(cli.Argument):
    APPLICATION_PACKAGE_PATH_PATTERNS = cli.ArgumentProperties(
        key='application_package_path_patterns',
        flags=('--path',),
        type=pathlib.Path,
        description=(
            'Path to artifact (*.ipa or *.pkg). Can be either a path literal, or '
            'a glob pattern to match projects in working directory.'
        ),
        argparse_kwargs={
            'required': False,
            'default': (pathlib.Path('**/*.ipa'), pathlib.Path('**/*.pkg')),
            'nargs': '+',
            'metavar': 'artifact-path',
        },
    )
    SUBMIT_TO_TESTFLIGHT = cli.ArgumentProperties(
        key='submit_to_testflight',
        flags=('--testflight', '-t'),
        type=bool,
        description='Submit an app for Testflight beta app review to allow external testing',
        argparse_kwargs={
            'required': False,
            'action': 'store_true',
        },
    )
    APPLE_ID = cli.ArgumentProperties(
        key='apple_id',
        flags=('--apple-id', '-u'),
        description=(
            'App Store Connect username used for application package validation '
            'and upload if App Store Connect API key is not specified'
        ),
        argparse_kwargs={'required': False},
    )
    APP_SPECIFIC_PASSWORD = cli.ArgumentProperties(
        key='app_specific_password',
        flags=('--password', '-p'),
        type=Types.AppSpecificPassword,
        description=(
            'App-specific password used for application package validation '
            'and upload if App Store Connect API Key is not specified. '
            f'Used together with {Colors.BRIGHT_BLUE("--apple-id")} '
            'and should match pattern "abcd-abcd-abcd-abcd". '
            'Create an app-specific password in the Security section of your Apple ID account. '
            'Learn more from https://support.apple.com/en-us/HT204397'
        ),
        argparse_kwargs={'required': False},
    )
    SKIP_PACKAGE_VALIDATION = cli.ArgumentProperties(
        key='skip_package_validation',
        flags=('--skip-package-validation',),
        type=Types.AppStoreConnectSkipPackageValidation,
        description=(
            'Skip package validation before uploading it to App Store Connect. '
            'Use this switch to opt out from running `altool --validate-app` before uploading '
            'package to App Store connect'
        ),
        argparse_kwargs={
            'required': False,
            'action': 'store_true',
        },
    )
    MAX_BUILD_PROCESSING_WAIT = cli.ArgumentProperties(
        key='max_build_processing_wait',
        flags=('--max-build-processing-wait',),
        type=Types.MaxBuildProcessingWait,
        description=(
            'Maximum amount of minutes to wait for the freshly uploaded build to be processed by '
            'Apple and retry submitting the build for beta review. If the processing is not finished '
            'within the specified timeframe, further submission will be terminated. '
            'Waiting will be skipped if the value is set to 0, further actions might fail '
            'if the build is not processed yet.'
        ),
        argparse_kwargs={
            'required': False,
        },
    )


class BuildArgument(cli.Argument):
    EXPIRED = cli.ArgumentProperties(
        key='expired',
        flags=('--expired',),
        type=bool,
        description='List only expired builds',
        argparse_kwargs={
            'required': False,
            'action': 'store_true',
        },
    )
    NOT_EXPIRED = cli.ArgumentProperties(
        key='not_expired',
        flags=('--not-expired',),
        type=bool,
        description='List only not expired builds',
        argparse_kwargs={
            'required': False,
            'action': 'store_true',
        },
    )
    BUILD_ID_RESOURCE_ID = cli.ArgumentProperties(
        key='build_id',
        type=ResourceId,
        description='Alphanumeric ID value of the Build',
    )
    BUILD_ID_RESOURCE_ID_OPTIONAL = cli.ArgumentProperties(
        key='build_id',
        flags=('--build-id',),
        type=ResourceId,
        description='Alphanumeric ID value of the Build',
        argparse_kwargs={'required': False},
    )
    PRE_RELEASE_VERSION = cli.ArgumentProperties(
        key='pre_release_version',
        flags=('--pre-release-version',),
        description=(
            'Version of the build published to Testflight '
            'that identifies an iteration of the bundle. '
            'The string can only contain one to three groups of numeric characters (0-9) '
            'separated by period in the format [Major].[Minor].[Patch]. '
            'For example `3.2.46`'
        ),
        argparse_kwargs={'required': False},
    )
    PROCESSING_STATE = cli.ArgumentProperties(
        key='processing_state',
        flags=('--processing-state',),
        type=BuildProcessingState,
        description='Build processing state',
        argparse_kwargs={
            'required': False,
            'choices': list(BuildProcessingState),
        },
    )
    BUILD_VERSION_NUMBER = cli.ArgumentProperties(
        key='build_version_number',
        flags=('--build-version-number',),
        type=int,
        description=(
            'Build version number is the version number of the uploaded build. '
            'For example `46`'
        ),
        argparse_kwargs={'required': False},
    )
    BETA_BUILD_LOCALIZATION_ID_RESOURCE_ID = cli.ArgumentProperties(
        key='localization_id',
        type=ResourceId,
        description='Alphanumeric ID value of the Beta Build Localization',
    )
    LOCALE_OPTIONAL = cli.ArgumentProperties(
        key='locale',
        flags=('--locale', '-l'),
        type=Locale,
        description=(
            'The locale code name for displaying localized "What\'s new" content in TestFlight. '
            'Learn more from https://developer.apple.com/documentation/appstoreconnectapi/'
            'betabuildlocalizationcreaterequest/data/attributes'
        ),
        argparse_kwargs={
            'required': False,
            'choices': list(Locale),
        },
    )
    LOCALE_DEFAULT = LOCALE_OPTIONAL.duplicate(
        description=(
            'The locale code name for displaying localized "What\'s new" content in TestFlight. '
            "In case not provided, application's primary locale from test information is used instead. "
            'Learn more from https://developer.apple.com/documentation/appstoreconnectapi/'
            'betabuildlocalizationcreaterequest/data/attributes'
        ),
    )
    WHATS_NEW = cli.ArgumentProperties(
        key='whats_new',
        flags=('--whats-new', '-n'),
        type=Types.WhatsNewArgument,
        description=(
            'Describe the changes and additions to the build and indicate '
            'the features you would like your users to tests.'
        ),
        argparse_kwargs={
            'required': False,
        },
    )
    BETA_BUILD_LOCALIZATIONS = cli.ArgumentProperties(
        key='beta_build_localizations',
        flags=('--beta-build-localizations',),
        type=Types.BetaBuildLocalizations,
        description=(
            "Localized beta test info for what's new in the uploaded build as a JSON encoded list. "
            f'For example, "{Colors.WHITE(Types.BetaBuildLocalizations.example_value)}". '
            f'See "{Colors.WHITE(LOCALE_OPTIONAL.flags[0])}" for possible locale options.'
        ),
        argparse_kwargs={
            'required': False,
        },
    )
    BETA_GROUP_NAMES_REQUIRED = cli.ArgumentProperties(
        key='beta_group_names',
        flags=('--beta-group',),
        type=str,
        description='Name of your Beta group',
        argparse_kwargs={
            'nargs': '+',
            'metavar': 'beta-group',
            'required': True,
        },
    )
    BETA_GROUP_NAMES_OPTIONAL = BETA_GROUP_NAMES_REQUIRED.duplicate(
        argparse_kwargs={
            'nargs': '+',
            'metavar': 'beta-group',
            'required': False,
        },
    )


class BundleIdArgument(cli.Argument):
    BUNDLE_ID_IDENTIFIER = cli.ArgumentProperties(
        key='bundle_id_identifier',
        description='Identifier of the Bundle ID. For example `com.example.app`',
    )
    BUNDLE_ID_IDENTIFIER_OPTIONAL = cli.ArgumentProperties(
        key='bundle_id_identifier',
        flags=('--bundle-id-identifier',),
        description='Identifier of the Bundle ID. For example `com.example.app`',
        argparse_kwargs={'required': False},
    )
    BUNDLE_ID_NAME = cli.ArgumentProperties(
        key='bundle_id_name',
        flags=('--name',),
        description=(
            'Name of the Bundle ID. If the resource is being created, '
            'the default will be deduced from given Bundle ID identifier.'
        ),
        argparse_kwargs={'required': False},
    )
    BUNDLE_ID_RESOURCE_ID = cli.ArgumentProperties(
        key='bundle_id_resource_id',
        type=ResourceId,
        description='Alphanumeric ID value of the Bundle ID',
    )
    BUNDLE_ID_RESOURCE_IDS = cli.ArgumentProperties(
        key='bundle_id_resource_ids',
        flags=('--bundle-ids',),
        type=ResourceId,
        description='Alphanumeric ID value of the Bundle ID',
        argparse_kwargs={
            'required': True,
            'nargs': '+',
            'metavar': 'bundle-identifier-id',
        },
    )
    PLATFORM = cli.ArgumentProperties(
        key='platform',
        flags=('--platform',),
        type=BundleIdPlatform,
        description='Bundle ID platform',
        argparse_kwargs={
            'required': False,
            'choices': list(BundleIdPlatform),
            'default': BundleIdPlatform.IOS,
        },
    )
    PLATFORM_OPTIONAL = cli.ArgumentProperties(
        key='platform',
        flags=('--platform',),
        type=BundleIdPlatform,
        description='Bundle ID platform',
        argparse_kwargs={
            'required': False,
            'choices': list(BundleIdPlatform),
        },
    )
    IDENTIFIER_STRICT_MATCH = cli.ArgumentProperties(
        key='bundle_id_identifier_strict_match',
        flags=('--strict-match-identifier',),
        type=bool,
        description=(
            'Only match Bundle IDs that have exactly the same identifier specified by '
            '`BUNDLE_ID_IDENTIFIER`. By default identifier `com.example.app` also matches '
            'Bundle IDs with identifier such as `com.example.app.extension`'
        ),
        argparse_kwargs={'required': False, 'action': 'store_true'},
    )


class DeviceArgument(cli.Argument):
    DEVICE_RESOURCE_IDS = cli.ArgumentProperties(
        key='device_resource_ids',
        flags=('--device-ids',),
        type=ResourceId,
        description='Alphanumeric ID value of the Device',
        argparse_kwargs={
            'required': True,
            'nargs': '+',
            'metavar': 'device-id',
        },
    )
    DEVICE_NAME = cli.ArgumentProperties(
        key='device_name',
        flags=('--name',),
        description='Name of the Device',
        argparse_kwargs={'required': False},
    )
    DEVICE_STATUS = cli.ArgumentProperties(
        key='device_status',
        flags=('--status',),
        type=DeviceStatus,
        description='Status of the Device',
        argparse_kwargs={
            'required': False,
            'choices': list(DeviceStatus),
        },
    )


class CertificateArgument(cli.Argument):
    CERTIFICATE_RESOURCE_ID = cli.ArgumentProperties(
        key='certificate_resource_id',
        type=ResourceId,
        description='Alphanumeric ID value of the Signing Certificate',
    )
    CERTIFICATE_RESOURCE_IDS = cli.ArgumentProperties(
        key='certificate_resource_ids',
        flags=('--certificate-ids',),
        type=ResourceId,
        description='Alphanumeric ID value of the Signing Certificate',
        argparse_kwargs={
            'required': True,
            'nargs': '+',
            'metavar': 'certificate-id',
        },
    )
    CERTIFICATE_TYPE = cli.ArgumentProperties(
        key='certificate_type',
        flags=('--type',),
        type=CertificateType,
        description='Type of the certificate',
        argparse_kwargs={
            'required': False,
            'choices': list(CertificateType),
            'default': CertificateType.IOS_DEVELOPMENT,
        },
    )
    CERTIFICATE_TYPE_OPTIONAL = cli.ArgumentProperties(
        key='certificate_type',
        flags=('--type',),
        type=CertificateType,
        description='Type of the certificate',
        argparse_kwargs={
            'required': False,
            'choices': list(CertificateType),
        },
    )
    PROFILE_TYPE_OPTIONAL = cli.ArgumentProperties(
        key='profile_type',
        flags=('--profile-type',),
        type=ProfileType,
        description='Type of the provisioning profile that the certificate is used with',
        argparse_kwargs={
            'required': False,
            'choices': list(ProfileType),
        },
    )
    DISPLAY_NAME = cli.ArgumentProperties(
        key='display_name',
        flags=('--display-name',),
        description='Code signing certificate display name',
        argparse_kwargs={'required': False},
    )
    PRIVATE_KEY = cli.ArgumentProperties(
        key='certificate_key',
        flags=('--certificate-key',),
        type=Types.CertificateKeyArgument,
        description=(
            f'Private key used to generate the certificate. '
            f'Used together with {Colors.BRIGHT_BLUE("--save")} '
            f'or {Colors.BRIGHT_BLUE("--create")} options.'
        ),
        argparse_kwargs={'required': False},
    )
    PRIVATE_KEY_PASSWORD = cli.ArgumentProperties(
        key='certificate_key_password',
        flags=('--certificate-key-password',),
        type=Types.CertificateKeyPasswordArgument,
        description=(
            f'Password of the private key used to generate the certificate. '
            f'Used together with {Colors.BRIGHT_BLUE("--certificate-key")} '
            f'or {Colors.BRIGHT_BLUE("--certificate-key-path")} options '
            f'if the provided key is encrypted.'
        ),
        argparse_kwargs={'required': False},
    )
    P12_CONTAINER_PASSWORD = cli.ArgumentProperties(
        key='p12_container_password',
        flags=('--p12-password',),
        description=(
            'If provided, the saved p12 container will be encrypted using this password. '
            f'Used together with {Colors.BRIGHT_BLUE("--save")} option.'
        ),
        argparse_kwargs={'required': False, 'default': ''},
    )


class ProfileArgument(cli.Argument):
    PROFILE_RESOURCE_ID = cli.ArgumentProperties(
        key='profile_resource_id',
        type=ResourceId,
        description='Alphanumeric ID value of the Profile',
    )
    PROFILE_TYPE = cli.ArgumentProperties(
        key='profile_type',
        flags=('--type',),
        type=ProfileType,
        description='Type of the provisioning profile',
        argparse_kwargs={
            'required': False,
            'choices': list(ProfileType),
            'default': ProfileType.IOS_APP_DEVELOPMENT,
        },
    )
    PROFILE_TYPE_OPTIONAL = cli.ArgumentProperties(
        key='profile_type',
        flags=('--type',),
        type=ProfileType,
        description='Type of the provisioning profile',
        argparse_kwargs={
            'required': False,
            'choices': list(ProfileType),
        },
    )
    PROFILE_STATE_OPTIONAL = cli.ArgumentProperties(
        key='profile_state',
        flags=('--state',),
        type=ProfileState,
        description='State of the provisioning profile',
        argparse_kwargs={
            'required': False,
            'choices': list(ProfileState),
        },
    )
    PROFILE_NAME = cli.ArgumentProperties(
        key='profile_name',
        flags=('--name',),
        description='Name of the provisioning profile',
        argparse_kwargs={'required': False},
    )


class CommonArgument(cli.Argument):
    CREATE_RESOURCE = cli.ArgumentProperties(
        key='create_resource',
        flags=('--create',),
        type=bool,
        description='Whether to create the resource if it does not exist yet',
        argparse_kwargs={'required': False, 'action': 'store_true'},
    )
    IGNORE_NOT_FOUND = cli.ArgumentProperties(
        key='ignore_not_found',
        flags=('--ignore-not-found',),
        type=bool,
        description='Do not raise exceptions if the specified resource does not exist.',
        argparse_kwargs={'required': False, 'action': 'store_true'},
    )
    SAVE = cli.ArgumentProperties(
        key='save',
        flags=('--save',),
        type=bool,
        description=(
            f'Whether to save the resources to disk. See '
            f'{Colors.CYAN(AppStoreConnectArgument.PROFILES_DIRECTORY.key.upper())} and '
            f'{Colors.CYAN(AppStoreConnectArgument.CERTIFICATES_DIRECTORY.key.upper())} '
            f'for more information.'
        ),
        argparse_kwargs={'required': False, 'action': 'store_true'},
    )
    PLATFORM = cli.ArgumentProperties(
        key='platform',
        flags=('--platform',),
        type=Platform,
        description='Apple operating systems',
        argparse_kwargs={
            'required': False,
            'choices': list(Platform),
        },
    )
