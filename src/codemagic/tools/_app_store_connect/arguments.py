import argparse
import json
import pathlib
import re
from argparse import ArgumentTypeError
from collections import Counter
from dataclasses import dataclass
from dataclasses import fields
from datetime import datetime
from datetime import timezone
from typing import List
from typing import Optional
from typing import Type

from cryptography.hazmat.primitives.serialization import load_pem_private_key

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
from codemagic.apple.resources import ReleaseType
from codemagic.apple.resources import ResourceId
from codemagic.cli import Colors
from codemagic.models import Certificate
from codemagic.models import ProvisioningProfile


@dataclass
class BetaBuildInfo:
    whats_new: str
    locale: Optional[Locale]


@dataclass
class AppStoreVersionInfo:
    platform: Platform
    copyright: Optional[str] = None
    earliest_release_date: Optional[datetime] = None
    release_type: Optional[ReleaseType] = None
    version_string: Optional[str] = None


@dataclass
class AppStoreVersionLocalizationInfo:
    description: Optional[str] = None
    keywords: Optional[str] = None
    locale: Optional[Locale] = None
    marketing_url: Optional[str] = None
    promotional_text: Optional[str] = None
    support_url: Optional[str] = None
    whats_new: Optional[str] = None


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
        def _apply_type(cls, non_typed_value: str) -> str:
            pem_private_key = cls.argument_type(non_typed_value)
            try:
                _ = load_pem_private_key(pem_private_key.encode(), None)
            except ValueError as ve:
                raise argparse.ArgumentTypeError('Provided value is not a valid PEM encoded private key') from ve
            return pem_private_key

    class CertificateKeyArgument(cli.EnvironmentArgumentValue[str]):
        environment_variable_key = 'CERTIFICATE_PRIVATE_KEY'

        @classmethod
        def _is_valid(cls, value: str) -> bool:
            return value.startswith('-----BEGIN ')

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

    class AppStoreConnectEnablePackageValidation(cli.TypedCliArgument[bool]):
        argument_type = bool
        environment_variable_key = 'APP_STORE_CONNECT_ENABLE_PACKAGE_VALIDATION'

    class AppStoreConnectSkipPackageUpload(cli.TypedCliArgument[bool]):
        argument_type = bool
        environment_variable_key = 'APP_STORE_CONNECT_SKIP_PACKAGE_UPLOAD'

    class AppStoreConnectDisableJwtCache(cli.TypedCliArgument[bool]):
        argument_type = bool
        environment_variable_key = 'APP_STORE_CONNECT_DISABLE_JWT_CACHE'

    class AltoolRetriesCount(cli.TypedCliArgument[int]):
        argument_type = int
        environment_variable_key = 'APP_STORE_CONNECT_ALTOOL_RETRIES'
        default_value = 10

        @classmethod
        def _is_valid(cls, value: int) -> bool:
            return value > 0

    class AltoolRetryWait(cli.TypedCliArgument[float]):
        argument_type = float
        environment_variable_key = 'APP_STORE_CONNECT_ALTOOL_RETRY_WAIT'
        default_value = 0.5

        @classmethod
        def _is_valid(cls, value: float) -> bool:
            return value >= 0

    class AltoolVerboseLogging(cli.TypedCliArgument[bool]):
        argument_type = bool
        environment_variable_key = 'APP_STORE_CONNECT_ALTOOL_VERBOSE_LOGGING'

    class MaxBuildProcessingWait(cli.TypedCliArgument[int]):
        argument_type = int
        environment_variable_key = 'APP_STORE_CONNECT_MAX_BUILD_PROCESSING_WAIT'
        default_value = 20

        @classmethod
        def _is_valid(cls, value: int) -> bool:
            return value >= 0

    class ApiUnauthorizedRetries(cli.TypedCliArgument[int]):
        argument_type = int
        environment_variable_key = 'APP_STORE_CONNECT_API_UNAUTHORIZED_RETRIES'
        default_value = 3

        @classmethod
        def _is_valid(cls, value: int) -> bool:
            return value > 0

    class ApiServerErrorRetries(cli.TypedCliArgument[int]):
        argument_type = int
        environment_variable_key = 'APP_STORE_CONNECT_API_SERVER_ERROR_RETRIES'
        default_value = 3

        @classmethod
        def _is_valid(cls, value: int) -> bool:
            return value > 0

    class EarliestReleaseDate(cli.TypedCliArgument[datetime]):
        argument_type = Type[datetime]

        @classmethod
        def validate(cls, value: datetime):
            if value <= datetime.utcnow().replace(tzinfo=timezone.utc):
                raise ArgumentTypeError(f'Provided value "{value}" is not valid, date cannot be in the past')
            elif (value.minute, value.second, value.microsecond) != (0, 0, 0):
                raise ArgumentTypeError((
                    f'Provided value "{value}" is not valid, '
                    f'only hour precision is allowed and '
                    f'minutes and seconds are not permitted'
                ))

        @classmethod
        def _apply_type(cls, non_typed_value: str) -> datetime:
            value = cli.CommonArgumentTypes.iso_8601_datetime(non_typed_value)
            cls.validate(value)
            return value

    class AppStoreVersionInfoArgument(cli.EnvironmentArgumentValue[AppStoreVersionInfo]):
        argument_type = List[AppStoreVersionInfo]
        environment_variable_key = 'APP_STORE_CONNECT_APP_STORE_VERSION_INFO'
        example_value = json.dumps({
            'platform': 'IOS',
            'copyright': '2008 Acme Inc.',
            'version_string': '1.0.8',
            'release_type': 'SCHEDULED',
            'earliest_release_date': '2021-11-10T14:00:00+00:00',
        })

        @classmethod
        def _apply_type(cls, non_typed_value: str) -> AppStoreVersionInfo:
            try:
                given_app_store_version_info = json.loads(non_typed_value)
                assert isinstance(given_app_store_version_info, dict)
            except (ValueError, AssertionError):
                raise ArgumentTypeError(f'Provided value {non_typed_value!r} is not a valid JSON encoded object')

            allowed_fields = {field.name for field in fields(AppStoreVersionInfo)}
            invalid_keys = given_app_store_version_info.keys() - allowed_fields
            if invalid_keys:
                keys = ', '.join(map(str, invalid_keys))
                raise ArgumentTypeError(f'Unknown App Store version option(s) {keys}')

            try:
                platform = Platform(given_app_store_version_info['platform'])
            except KeyError:
                platform = AppStoreVersionArgument.PLATFORM.get_default()
            except ValueError as ve:
                raise ArgumentTypeError(f'Invalid App Store version info: {ve}')
            app_store_version_info = AppStoreVersionInfo(platform=platform)

            try:
                given_earliest_release_date = given_app_store_version_info['given_app_store_version_info']
                app_store_version_info.earliest_release_date = \
                    cli.CommonArgumentTypes.iso_8601_datetime(given_earliest_release_date)
                Types.EarliestReleaseDate.validate(app_store_version_info.earliest_release_date)
            except KeyError:
                pass
            except ArgumentTypeError as ate:
                raise ArgumentTypeError(f'Invalid "earliest_release_date" in App Store version info: {ate}') from ate

            if 'release_type' in given_app_store_version_info:
                try:
                    app_store_version_info.release_type = ReleaseType(given_app_store_version_info['release_type'])
                except ValueError as ve:
                    raise ArgumentTypeError(f'Invalid App Store version info: {ve}')

            if 'copyright' in given_app_store_version_info:
                app_store_version_info.copyright = given_app_store_version_info['copyright']
            if 'version_string' in given_app_store_version_info:
                app_store_version_info.version_string = given_app_store_version_info['version_string']

            return app_store_version_info

    class AppStoreVersionLocalizationInfoArgument(cli.EnvironmentArgumentValue[List[AppStoreVersionLocalizationInfo]]):
        argument_type = List[AppStoreVersionLocalizationInfo]
        environment_variable_key = 'APP_STORE_CONNECT_APP_STORE_VERSION_LOCALIZATIONS'
        example_value = json.dumps([{
            'description': 'App description',
            'keywords': 'keyword, other keyword',
            'locale': 'en-US',
            'marketing_url': 'https://example.com',
            'promotional_text': 'Promotional text',
            'support_url': 'https://example.com',
            'whats_new': 'Fixes an issue ...',
        }])

        @classmethod
        def _apply_type(cls, non_typed_value: str) -> List[AppStoreVersionLocalizationInfo]:
            try:
                given_localization_infos = json.loads(non_typed_value)
                assert isinstance(given_localization_infos, list)
            except (ValueError, AssertionError):
                raise ArgumentTypeError(f'Provided value {non_typed_value!r} is not a valid JSON encoded list')

            app_store_version_localization_infos: List[AppStoreVersionLocalizationInfo] = []
            error_prefix = 'Invalid App Store Version localization'
            for i, given_localization_info in enumerate(given_localization_infos):
                try:
                    locale: Optional[Locale] = Locale(given_localization_info['locale'])
                except KeyError:
                    locale = None
                except ValueError as ve:  # Invalid locale
                    raise ArgumentTypeError(f'{error_prefix} on index {i}, {ve} in {given_localization_info!r}')
                except TypeError:  # Given beta build localization is not a dictionary
                    raise ArgumentTypeError(f'{error_prefix} value {given_localization_info!r} on index {i}')

                localization_info = AppStoreVersionLocalizationInfo(
                    description=given_localization_info.get('description'),
                    keywords=given_localization_info.get('keywords'),
                    locale=locale,
                    marketing_url=given_localization_info.get('marketing_url'),
                    promotional_text=given_localization_info.get('promotional_text'),
                    support_url=given_localization_info.get('support_url'),
                    whats_new=given_localization_info.get('whats_new'),
                )

                if set(localization_info.__dict__.values()) == {None}:
                    raise ArgumentTypeError(f'{error_prefix} value {given_localization_info!r} on index {i}')
                app_store_version_localization_infos.append(localization_info)

            locales = Counter(info.locale for info in app_store_version_localization_infos)
            duplicate_locales = {
                locale.value if locale else 'primary'
                for locale, uses in locales.items()
                if uses > 1
            }
            if duplicate_locales:
                raise ArgumentTypeError((
                    f'Ambiguous definitions for locale(s) {", ".join(duplicate_locales)}. '
                    'Please define App Store Version localization for each locale exactly once.'
                ))

            return app_store_version_localization_infos

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
_LOCALE_CODES_URL = \
    'https://developer.apple.com/documentation/appstoreconnectapi/betabuildlocalizationcreaterequest/data/attributes'


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
    UNAUTHORIZED_REQUEST_RETRIES = cli.ArgumentProperties(
        key='unauthorized_request_retries',
        flags=('--api-unauthorized-retries', '-r'),
        type=Types.ApiUnauthorizedRetries,
        description=(
            'Specify how many times the App Store Connect API request '
            'should be retried in case the called request fails due to an '
            'authentication error (401 Unauthorized response from the server). '
            'In case of the above authentication error, the request is retried using'
            'a new JSON Web Token as many times until the number of retries '
            'is exhausted.'
        ),
        argparse_kwargs={
            'required': False,
        },
    )
    SERVER_ERROR_RETRIES = cli.ArgumentProperties(
        key='server_error_retries',
        flags=('--api-server-error-retries',),
        type=Types.ApiServerErrorRetries,
        description=(
            'Specify how many times the App Store Connect API request '
            'should be retried in case the called request fails due to a '
            'server error (response with status code 5xx). '
            'In case of server error, the request is retried until '
            'the number of retries is exhausted.'
        ),
        argparse_kwargs={
            'required': False,
        },
    )
    DISABLE_JWT_CACHE = cli.ArgumentProperties(
        key='disable_jwt_cache',
        flags=('--disable-jwt-cache',),
        description=(
            'Turn off caching App Store Connect JSON Web Tokens to disk. '
            'By default generated tokens are cached to disk to be reused between '
            'separate processes, which can can reduce number of '
            'false positive authentication errors from App Store Connect API.'
        ),
        type=Types.AppStoreConnectDisableJwtCache,
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
    APP_STORE_VERSION_INFO = cli.ArgumentProperties(
        key='app_store_version_info',
        flags=('--app-store-version-info', '-vi'),
        type=Types.AppStoreVersionInfoArgument,
        description=(
            'General App information and version release options for App Store version submission '
            'as a JSON encoded object. Alternative to individually defining '
            f'`{Colors.BRIGHT_BLUE("--platform")}`, `{Colors.BRIGHT_BLUE("--copyright")}`, '
            f'`{Colors.BRIGHT_BLUE("--earliest-release-date")}`, `{Colors.BRIGHT_BLUE("--release-type")}` '
            f'and `{Colors.BRIGHT_BLUE("--version-string")}`. '
            f'For example, "{Colors.WHITE(Types.AppStoreVersionInfoArgument.example_value)}". '
            'Definitions from the JSON will be overridden by dedicated CLI options if provided.'
        ),
        argparse_kwargs={
            'required': False,
        },
    )
    APP_STORE_VERSION_SUBMISSION_ID = cli.ArgumentProperties(
        key='app_store_version_submission_id',
        type=ResourceId,
        description='UUID value of the App Store Version Submission',
    )
    COPYRIGHT = cli.ArgumentProperties(
        key='copyright',
        flags=('--copyright',),
        description=(
            'The name of the person or entity that owns the exclusive rights to your app, '
            f'preceded by the year the rights were obtained (for example, `{Colors.WHITE("2008 Acme Inc.")}`). '
            'Do not provide a URL.'
        ),
        argparse_kwargs={'required': False},
    )
    EARLIEST_RELEASE_DATE = cli.ArgumentProperties(
        key='earliest_release_date',
        flags=('--earliest-release-date',),
        type=Types.EarliestReleaseDate,
        description=(
            f'Specify earliest return date for scheduled release type '
            f'(see `{Colors.BRIGHT_BLUE("--release-type")}` configuration option). '
            f'Timezone aware ISO8601 timestamp with hour precision, '
            f'for example "{Colors.WHITE("2021-11-10T14:00:00+00:00")}".'
        ),
        argparse_kwargs={'required': False},
    )
    PLATFORM = cli.ArgumentProperties(
        key='platform',
        flags=('--platform', '--app-store-version-platform'),
        type=Platform,
        description='App Store Version platform',
        argparse_kwargs={
            'required': False,
            'choices': list(Platform),
            'default': Platform.IOS,
        },
    )
    PLATFORM_OPTIONAL = cli.ArgumentProperties.duplicate(
        PLATFORM,
        argparse_kwargs={
            'required': False,
            'choices': list(Platform),
        },
    )
    RELEASE_TYPE = cli.ArgumentProperties(
        key='release_type',
        flags=('--release-type',),
        type=ReleaseType,
        description=(
            'Choose when to release the app. You can either manually release the app at a later date on '
            'the App Store Connect website, or the app version can be automatically released right after '
            'it has been approved by App Review.'
        ),
        argparse_kwargs={
            'required': False,
            'choices': list(ReleaseType),
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
            f'For example `{Colors.WHITE("3.2.46")}`'
        ),
        argparse_kwargs={'required': False},
    )


class ReviewSubmissionArgument(cli.Argument):
    APP_CUSTOM_PRODUCT_PAGE_VERSION_ID = cli.ArgumentProperties(
        key='app_custom_product_page_version_id',
        flags=('--app-custom-product-page-version-id',),
        description='UUID value of custom product page',
        type=ResourceId,
    )
    APP_EVENT_ID = cli.ArgumentProperties(
        key='app_event_id',
        flags=('--app-event-id',),
        description='UUID value of app event',
        type=ResourceId,
    )
    APP_STORE_VERSION_ID = cli.ArgumentProperties(
        key='app_store_version_id',
        flags=('--version-id', '--app-store-version-id'),
        type=ResourceId,
        description='UUID value of the App Store Version',
    )
    APP_STORE_VERSION_EXPERIMENT_ID = cli.ArgumentProperties(
        key='app_store_version_experiment_id',
        flags=('--app-store-version-experiment-id',),
        type=ResourceId,
        description='UUID value of the App Store Version experiment',
    )
    REVIEW_SUBMISSION_ID = cli.ArgumentProperties(
        key='review_submission_id',
        type=ResourceId,
        description='UUID value of the review submission',
    )


class AppStoreVersionLocalizationArgument(cli.Argument):
    APP_STORE_VERSION_LOCALIZATION_ID = cli.ArgumentProperties(
        key='app_store_version_localization_id',
        type=ResourceId,
        description='UUID value of the App Store Version localization',
    )
    LOCALE = cli.ArgumentProperties(
        key='locale',
        type=Locale,
        description=(
            'The locale code name for App Store metadata in different languages. '
            f'See available locale code names from {_LOCALE_CODES_URL}'
        ),
        argparse_kwargs={
            'choices': list(Locale),
        },
    )
    LOCALE_DEFAULT = cli.ArgumentProperties.duplicate(
        LOCALE,
        flags=('--locale', '-l'),
        description=(
            'The locale code name for App Store metadata in different languages. '
            "In case not provided, application's primary locale is used instead. "
            f'Learn more from {_LOCALE_CODES_URL}'
        ),
        argparse_kwargs={
            'required': False,
            'choices': list(Locale),
        },
    )
    DESCRIPTION = cli.ArgumentProperties(
        key='description',
        flags=('--description', '-d'),
        description='A description of your app, detailing features and functionality.',
        argparse_kwargs={
            'required': False,
        },
    )
    KEYWORDS = cli.ArgumentProperties(
        key='keywords',
        flags=('--keywords', '-k'),
        description=(
            'Include one or more keywords that describe your app. Keywords make '
            'App Store search results more accurate. Separate keywords with an '
            'English comma, Chinese comma, or a mix of both.'
        ),
        argparse_kwargs={
            'required': False,
        },
    )
    MARKETING_URL = cli.ArgumentProperties(
        key='marketing_url',
        flags=('--marketing-url',),
        description=(
            'A URL with marketing information about your app. '
            'This URL will be visible on the App Store.'
        ),
        argparse_kwargs={
            'required': False,
        },
    )
    PROMOTIONAL_TEXT = cli.ArgumentProperties(
        key='promotional_text',
        flags=('--promotional-text',),
        description=(
            'Promotional text lets you inform your App Store visitors of any current '
            'app features without requiring an updated submission. This text will '
            'appear above your description on the App Store for customers with devices '
            'running iOS 11 or later, and macOS 10.13 or later.'
        ),
        argparse_kwargs={
            'required': False,
        },
    )
    SUPPORT_URL = cli.ArgumentProperties(
        key='support_url',
        flags=('--support-url',),
        description=(
            'A URL with support information for your app. '
            'This URL will be visible on the App Store.'
        ),
        argparse_kwargs={
            'required': False,
        },
    )
    WHATS_NEW = cli.ArgumentProperties(
        key='whats_new',
        flags=('--whats-new', '-n'),
        type=Types.WhatsNewArgument,
        description=(
            "Describe what's new in this version of your app, "
            'such as new features, improvements, and bug fixes.'
        ),
        argparse_kwargs={
            'required': False,
        },
    )
    APP_STORE_VERSION_LOCALIZATION_INFOS = cli.ArgumentProperties(
        key='app_store_version_localizations',
        flags=('--app-store-version-localizations', '-vl'),
        type=Types.AppStoreVersionLocalizationInfoArgument,
        description=(
            'Localized App Store version meta information for App Store version submission '
            'as a JSON encoded list. Alternative to individually defining version release notes '
            f'and other options via dedicated CLI options such as `{Colors.BRIGHT_BLUE("--whats-new")}`. '
            'Definitions for duplicate locales are not allowed. '
            f'For example, "{Colors.WHITE(Types.AppStoreVersionLocalizationInfoArgument.example_value)}"'
        ),
        argparse_kwargs={
            'required': False,
        },
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
        description='Enable submission of an app for Testflight beta app review to allow external testing.',
        argparse_kwargs={
            'required': False,
            'action': 'store_true',
        },
    )
    SUBMIT_TO_APP_STORE = cli.ArgumentProperties(
        key='submit_to_app_store',
        flags=('--app-store', '-a'),
        type=bool,
        description='Enable submission of an app to App Store app review procedure.',
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
    ENABLE_PACKAGE_VALIDATION = cli.ArgumentProperties(
        key='enable_package_validation',
        flags=('--enable-package-validation', '-ev'),
        type=Types.AppStoreConnectEnablePackageValidation,
        description=(
            'Validate package before uploading it to App Store Connect. '
            'Use this switch to enable running `altool --validate-app` before uploading '
            'the package to App Store connect'
        ),
        argparse_kwargs={
            'required': False,
            'action': 'store_true',
        },
    )
    SKIP_PACKAGE_VALIDATION = cli.ArgumentProperties(
        key='skip_package_validation',
        flags=('--skip-package-validation', '-sv'),
        type=Types.AppStoreConnectSkipPackageValidation,
        description=(
            f'{Colors.BOLD("Deprecated")}. '
            f'Starting from version `0.14.0` package validation before '
            'uploading it to App Store Connect is disabled by default.'
        ),
        argparse_kwargs={
            'required': False,
            'action': 'store_true',
        },
    )
    SKIP_PACKAGE_UPLOAD = cli.ArgumentProperties(
        key='skip_package_upload',
        flags=('--skip-package-upload', '-su'),
        type=Types.AppStoreConnectSkipPackageUpload,
        description=(
            'Skip package upload before doing any other TestFlight or App Store related actions. '
            'Using this switch will opt out from running `altool --upload-app` as part of publishing '
            'action. Use this option in case your application package is already uploaded to App Store.'
        ),
        argparse_kwargs={
            'required': False,
            'action': 'store_true',
        },
    )
    LOCALE_DEFAULT = cli.ArgumentProperties(
        key='locale',
        flags=('--locale', '-l'),
        type=Locale,
        description=(
            'The locale code name for App Store metadata in different languages, '
            'or for displaying localized "What\'s new" content in TestFlight. '
            "In case not provided, application's primary locale is used instead. "
            f'Learn more from {_LOCALE_CODES_URL}'
        ),
        argparse_kwargs={
            'required': False,
            'choices': list(Locale),
        },
    )
    WHATS_NEW = cli.ArgumentProperties(
        key='whats_new',
        flags=('--whats-new', '-n'),
        type=Types.WhatsNewArgument,
        description=(
            'Release notes either for TestFlight or App Store review submission. '
            "Describe what's new in this version of your app, "
            'such as new features, improvements, and bug fixes.'
        ),
        argparse_kwargs={
            'required': False,
        },
    )
    MAX_BUILD_PROCESSING_WAIT = cli.ArgumentProperties(
        key='max_build_processing_wait',
        flags=('--max-build-processing-wait', '-w'),
        type=Types.MaxBuildProcessingWait,
        description=(
            'Maximum amount of minutes to wait for the freshly uploaded build to be processed by '
            'Apple and retry submitting the build for (beta) review. Works in conjunction with '
            'TestFlight beta review submission, or App Store review submission and operations that '
            'depend on either one of those. If the processing is not finished '
            'within the specified timeframe, further submission will be terminated. '
            'Waiting will be skipped if the value is set to 0, further actions might fail '
            'if the build is not processed yet.'
        ),
        argparse_kwargs={
            'required': False,
        },
    )
    ALTOOL_VERBOSE_LOGGING = cli.ArgumentProperties(
        key='altool_verbose_logging',
        flags=('--altool-verbose-logging',),
        type=Types.AltoolVerboseLogging,
        description=(
            'Show verbose log output when launching Application Loader tool. '
            'That is add `--verbose` flag to `altool` invocations when either validating '
            'the package, or while uploading the pakcage to App Store Connect.'
        ),
        argparse_kwargs={
            'required': False,
            'action': 'store_true',
        },
    )
    ALTOOL_RETRIES_COUNT = cli.ArgumentProperties(
        key='altool_retries_count',
        flags=('--altool-retries',),
        type=Types.AltoolRetriesCount,
        description=(
            'Define how many times should the package validation or upload action be attempted in case it '
            'failed due to a known `altool` issue (authentication failure or request timeout).'
        ),
        argparse_kwargs={
            'required': False,
        },
    )
    ALTOOL_RETRY_WAIT = cli.ArgumentProperties(
        key='altool_retry_wait',
        flags=('--altool-retry-wait',),
        type=Types.AltoolRetryWait,
        description=(
            'For how long (in seconds) should the tool wait between the retries of package validation or '
            'upload action retries in case they failed due to a known `altool` issues '
            '(authentication failure or request timeout). '
            f'See also {cli.ArgumentProperties.get_flag(ALTOOL_RETRIES_COUNT)} for more configuration options.'
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
        description=(
            f'List only expired builds. Mutually exclusive with option `{Colors.BRIGHT_BLUE("--not-expired")}`.'
        ),
        argparse_kwargs={
            'required': False,
            'action': 'store_true',
        },
    )
    NOT_EXPIRED = cli.ArgumentProperties(
        key='not_expired',
        flags=('--not-expired',),
        type=bool,
        description=(
            f'List only not expired builds. Mutually exclusive with option `{Colors.BRIGHT_BLUE("--expired")}`.'
        ),
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
        description=(
            'Build version number is the version number of the uploaded build. '
            'For example `46` or `1.0.13.5`.'
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
            f'Learn more from {_LOCALE_CODES_URL}'
        ),
        argparse_kwargs={
            'required': False,
            'choices': list(Locale),
        },
    )
    LOCALE_DEFAULT = cli.ArgumentProperties.duplicate(
        LOCALE_OPTIONAL,
        description=(
            'The locale code name for displaying localized "What\'s new" content in TestFlight. '
            "In case not provided, application's primary locale from test information is used instead. "
            f'Learn more from {_LOCALE_CODES_URL}'
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
            f'See "{Colors.WHITE(cli.ArgumentProperties.get_flag(LOCALE_OPTIONAL))}" for possible locale options.'
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
    BETA_GROUP_NAMES_OPTIONAL = cli.ArgumentProperties.duplicate(
        BETA_GROUP_NAMES_REQUIRED,
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
        argparse_kwargs={'required': True},
    )
    DEVICE_NAME_OPTIONAL = cli.ArgumentProperties.duplicate(
        DEVICE_NAME,
        argparse_kwargs={'required': False},
    )
    DEVICE_UDID = cli.ArgumentProperties(
        key='device_udid',
        flags=('--udid',),
        description='Device ID (UDID)',
        argparse_kwargs={'required': True},
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
    CERTIFICATE_TYPES_OPTIONAL = cli.ArgumentProperties(
        key='certificate_types',
        flags=('--type',),
        type=CertificateType,
        description='Type of the certificate',
        argparse_kwargs={
            'required': False,
            'choices': list(CertificateType),
            'nargs': '+',
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
    P12_CONTAINER_SAVE_PATH = cli.ArgumentProperties(
        key='p12_container_save_path',
        flags=('--p12-path',),
        type=cli.CommonArgumentTypes.non_existing_path,
        description=(
            'If provided, the exported p12 container will saved at this path. '
            'Otherwise it will be saved with a random name in the directory specified '
            f'by {Colors.BRIGHT_BLUE("--certificates-dir")}. '
            f'Used together with {Colors.BRIGHT_BLUE("--save")} option.'
        ),
        argparse_kwargs={'required': False},
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


class ArgumentGroups:
    ADD_BETA_TEST_INFO_OPTIONAL_ARGUMENTS = (
        BuildArgument.BETA_BUILD_LOCALIZATIONS,
        BuildArgument.LOCALE_DEFAULT,
        BuildArgument.WHATS_NEW,
    )
    ADD_BUILD_TO_BETA_GROUPS_OPTIONAL_ARGUMENTS = (
        BuildArgument.BETA_GROUP_NAMES_OPTIONAL,
    )
    ALTOOL_CONFIGURATION_ARGUMENTS = (
        PublishArgument.ALTOOL_RETRIES_COUNT,
        PublishArgument.ALTOOL_RETRY_WAIT,
        PublishArgument.ALTOOL_VERBOSE_LOGGING,
    )
    LIST_BUILDS_FILTERING_ARGUMENTS = (
        BuildArgument.BUILD_ID_RESOURCE_ID_OPTIONAL,
        BuildArgument.BUILD_VERSION_NUMBER,
        BuildArgument.EXPIRED,
        BuildArgument.NOT_EXPIRED,
        BuildArgument.PRE_RELEASE_VERSION,
        BuildArgument.PROCESSING_STATE,
    )
    PACKAGE_UPLOAD_ARGUMENTS = (
        PublishArgument.ENABLE_PACKAGE_VALIDATION,
        PublishArgument.SKIP_PACKAGE_VALIDATION,
        PublishArgument.SKIP_PACKAGE_UPLOAD,
    )
    SUBMIT_TO_APP_STORE_OPTIONAL_ARGUMENTS = (
        PublishArgument.MAX_BUILD_PROCESSING_WAIT,
        # Generic App Store Version information arguments
        AppStoreVersionArgument.APP_STORE_VERSION_INFO,
        AppStoreVersionArgument.COPYRIGHT,
        AppStoreVersionArgument.EARLIEST_RELEASE_DATE,
        AppStoreVersionArgument.PLATFORM,
        AppStoreVersionArgument.RELEASE_TYPE,
        AppStoreVersionArgument.VERSION_STRING,
        # Localized App Store Version arguments
        AppStoreVersionLocalizationArgument.DESCRIPTION,
        AppStoreVersionLocalizationArgument.KEYWORDS,
        AppStoreVersionLocalizationArgument.LOCALE_DEFAULT,
        AppStoreVersionLocalizationArgument.MARKETING_URL,
        AppStoreVersionLocalizationArgument.PROMOTIONAL_TEXT,
        AppStoreVersionLocalizationArgument.SUPPORT_URL,
        AppStoreVersionLocalizationArgument.WHATS_NEW,
        AppStoreVersionLocalizationArgument.APP_STORE_VERSION_LOCALIZATION_INFOS,
    )
    SUBMIT_TO_TESTFLIGHT_OPTIONAL_ARGUMENTS = (
        PublishArgument.MAX_BUILD_PROCESSING_WAIT,
    )
