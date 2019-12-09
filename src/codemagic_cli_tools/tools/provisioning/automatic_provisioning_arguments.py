import pathlib

from codemagic_cli_tools import cli
from codemagic_cli_tools.apple.app_store_connect import AppStoreConnectApiClient
from codemagic_cli_tools.apple.app_store_connect import IssuerId
from codemagic_cli_tools.apple.app_store_connect import KeyIdentifier
from codemagic_cli_tools.apple.resources import BundleIdPlatform, DeviceStatus
from codemagic_cli_tools.apple.resources import ResourceId


class Types:
    class BundleIdArgument(cli.TypedCliArgument[str]):
        pass

    class IssuerIdArgument(cli.EnvironmentArgumentValue[IssuerId]):
        argument_type = IssuerId
        environment_variable_key = 'APP_STORE_CONNECT_ISSUER_ID'

    class KeyIdentifierArgument(cli.EnvironmentArgumentValue[KeyIdentifier]):
        argument_type = KeyIdentifier
        environment_variable_key = 'APP_STORE_CONNECT_KEY_IDENTIFIER'

    class PrivateKeyArgument(cli.EnvironmentArgumentValue[str]):
        environment_variable_key = 'APP_STORE_CONNECT_PRIVATE_KEY'
        alternative_to = 'PRIVATE_KEY_PATH'

        @classmethod
        def _is_valid(cls, value: str) -> bool:
            return value.startswith('-----BEGIN PRIVATE KEY-----')

    class PrivateKeyPathArgument(cli.TypedCliArgument[pathlib.Path]):
        environment_variable_key = 'APP_STORE_CONNECT_PRIVATE_KEY_PATH'
        alternative_to = 'PRIVATE_KEY'
        argument_type = pathlib.Path

        @classmethod
        def _is_valid(cls, value: pathlib.Path) -> bool:
            return value.exists() and value.is_file()


_API_DOCS_REFERENCE = f'Learn more at {AppStoreConnectApiClient.API_KEYS_DOCS_URL}.'


class AutomaticProvisioningArgument(cli.Argument):
    LOG_REQUESTS = cli.ArgumentProperties(
        key='log_requests',
        flags=('--log-api-calls',),
        type=bool,
        description='Turn on logging for App Store Connect API HTTP requests',
        argparse_kwargs={'required': False, 'action': 'store_true'},
    )
    ISSUER_ID = cli.ArgumentProperties(
        key='issuer_id',
        flags=('--issuer-id',),
        type=Types.IssuerIdArgument,
        description=f'App Store Connect API Key Issuer ID. Identifies the issuer '
                    f'who created the authentication token. {_API_DOCS_REFERENCE}',
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
    PRIVATE_KEY_PATH = cli.ArgumentProperties(
        key='private_key_path',
        flags=('--private-key-path',),
        type=Types.PrivateKeyPathArgument,
        description=f'Path to the App Store Connect API private key. {_API_DOCS_REFERENCE}',
        argparse_kwargs={'required': False},
    )


class BundleIdActionArgument(cli.Argument):
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
        flags=('--bundle-id-name',),
        description='Name of the Bundle ID. If the resource is being created, '
                    'the default will be deduced from given Bundle ID identifier.',
        argparse_kwargs={'required': False},
    )
    BUNDLE_ID_RESOURCE_ID = cli.ArgumentProperties(
        key='bundle_id_resource_id',
        type=ResourceId,
        description='Alphanumeric ID value of the Bundle ID',
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


class DeviceActionArgument(cli.Argument):
    DEVICE_NAME = cli.ArgumentProperties(
        key='device_name',
        flags=('--device_name',),
        description='Name of the Device',
        argparse_kwargs={'required': False}
    )
    DEVICE_PLATFORM = cli.ArgumentProperties(
        key='device_platform',
        type=BundleIdPlatform,
        flags=('--device_platform',),
        description='Platform of the Device',
        argparse_kwargs={
            'required': False,
            'choices': list(BundleIdPlatform),
        }
    )
    DEVICE_STATUS = cli.ArgumentProperties(
        key='device_status',
        flags=('--device_status',),
        type=DeviceStatus,
        description='Status of the Device',
        argparse_kwargs={
            'required': False,
            'choices': list(DeviceStatus),
        }
    )


class CommonActionArgument(cli.Argument):
    CREATE_RESOURCE = cli.ArgumentProperties(
        key='create_resource',
        flags=('--create',),
        type=bool,
        description='Whether to create the resource if it does not exist yet',
        argparse_kwargs={'required': False, 'action': 'store_true', 'default': False},
    )
    IGNORE_NOT_FOUND = cli.ArgumentProperties(
        key='ignore_not_found',
        flags=('--ignore-not-found',),
        type=bool,
        description='Do not raise exceptions if the specified resource does not exist.',
        argparse_kwargs={'required': False, 'action': 'store_true', 'default': False},
    )
    JSON_OUTPUT = cli.ArgumentProperties(
        key='json_output',
        flags=('--json',),
        type=bool,
        description='Whether to show the resource in JSON format',
        argparse_kwargs={'required': False, 'action': 'store_true', 'default': False},
    )
