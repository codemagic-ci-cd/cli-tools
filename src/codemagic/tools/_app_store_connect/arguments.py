import pathlib

from codemagic import cli
from codemagic.apple.app_store_connect import AppStoreConnectApiClient
from codemagic.apple.app_store_connect import IssuerId
from codemagic.apple.app_store_connect import KeyIdentifier
from codemagic.apple.resources import BundleIdPlatform
from codemagic.apple.resources import CertificateType
from codemagic.apple.resources import DeviceStatus
from codemagic.apple.resources import ProfileState
from codemagic.apple.resources import ProfileType
from codemagic.apple.resources import ResourceId
from codemagic.cli import Colors
from codemagic.models import Certificate
from codemagic.models import ProvisioningProfile


class Types:
    class IssuerIdArgument(cli.EnvironmentArgumentValue[IssuerId]):
        argument_type = IssuerId
        environment_variable_key = 'APP_STORE_CONNECT_ISSUER_ID'

    class KeyIdentifierArgument(cli.EnvironmentArgumentValue[KeyIdentifier]):
        argument_type = KeyIdentifier
        environment_variable_key = 'APP_STORE_CONNECT_KEY_IDENTIFIER'

    class PrivateKeyArgument(cli.EnvironmentArgumentValue[str]):
        environment_variable_key = 'APP_STORE_CONNECT_PRIVATE_KEY'

        @classmethod
        def _is_valid(cls, value: str) -> bool:
            return value.startswith('-----BEGIN ')

    class CertificateKeyArgument(PrivateKeyArgument):
        environment_variable_key = 'CERTIFICATE_PRIVATE_KEY'

    class CertificateKeyPasswordArgument(cli.EnvironmentArgumentValue):
        environment_variable_key = 'CERTIFICATE_PRIVATE_KEY_PASSWORD'


_API_DOCS_REFERENCE = f'Learn more at {AppStoreConnectApiClient.API_KEYS_DOCS_URL}.'


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
        description=f'App Store Connect API private key. {_API_DOCS_REFERENCE}',
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


class BundleIdArgument(cli.Argument):
    BUNDLE_ID_IDENTIFIER = cli.ArgumentProperties(
        key='bundle_id_identifier',
        description='Identifier of the Bundle ID',
    )
    BUNDLE_ID_IDENTIFIER_OPTIONAL = cli.ArgumentProperties(
        key='bundle_id_identifier',
        flags=('--bundle-id-identifier',),
        description='Identifier of the Bundle ID',
        argparse_kwargs={'required': False}
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
            'metavar': 'bundle-identifier-id'
        }
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


class DeviceArgument(cli.Argument):
    DEVICE_RESOURCE_IDS = cli.ArgumentProperties(
        key='device_resource_ids',
        flags=('--device-ids',),
        type=ResourceId,
        description='Alphanumeric ID value of the Device',
        argparse_kwargs={
            'required': True,
            'nargs': '+',
            'metavar': 'device-id'
        }
    )
    DEVICE_NAME = cli.ArgumentProperties(
        key='device_name',
        flags=('--name',),
        description='Name of the Device',
        argparse_kwargs={'required': False}
    )
    DEVICE_STATUS = cli.ArgumentProperties(
        key='device_status',
        flags=('--status',),
        type=DeviceStatus,
        description='Status of the Device',
        argparse_kwargs={
            'required': False,
            'choices': list(DeviceStatus),
        }
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
            'metavar': 'certificate-id'
        }
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
        }
    )
    CERTIFICATE_TYPE_OPTIONAL = cli.ArgumentProperties(
        key='certificate_type',
        flags=('--type',),
        type=CertificateType,
        description='Type of the certificate',
        argparse_kwargs={
            'required': False,
            'choices': list(CertificateType),
        }
    )
    DISPLAY_NAME = cli.ArgumentProperties(
        key='display_name',
        flags=('--display-name',),
        description='Code signing certificate display name',
        argparse_kwargs={'required': False}
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
            'default': ProfileType.IOS_APP_DEVELOPMENT
        }
    )
    PROFILE_TYPE_OPTIONAL = cli.ArgumentProperties(
        key='profile_type',
        flags=('--type',),
        type=ProfileType,
        description='Type of the provisioning profile',
        argparse_kwargs={
            'required': False,
            'choices': list(ProfileType),
        }
    )
    PROFILE_STATE_OPTIONAL = cli.ArgumentProperties(
        key='profile_state',
        flags=('--state',),
        type=ProfileState,
        description='State of the provisioning profile',
        argparse_kwargs={
            'required': False,
            'choices': list(ProfileState),
        }
    )
    PROFILE_NAME = cli.ArgumentProperties(
        key='profile_name',
        flags=('--name',),
        description='Name of the provisioning profile',
        argparse_kwargs={'required': False}
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
