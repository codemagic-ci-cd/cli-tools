import pathlib

from codemagic import cli
from codemagic.cli import Colors

from . import argument_types


class AndroidKeystoreArgument(cli.Argument):
    KEYSTORE_PATH = cli.ArgumentProperties(
        key='keystore_path',
        flags=('-k', '--ks', '--keystore'),
        type=pathlib.Path,
        description='Path where your keystore should be created or read from',
        argparse_kwargs={'required': True},
    )
    KEYSTORE_PASSWORD = cli.ArgumentProperties(
        key='keystore_password',
        flags=('-p', '--ks-pass', '--keystore-pass'),
        type=argument_types.KeystorePassword,
        description='Secure password for your keystore',
        argparse_kwargs={'required': True},
    )
    KEY_ALIAS_OPTIONAL = cli.ArgumentProperties(
        key='key_alias',
        flags=('-a', '--ks-key-alias', '--alias'),
        description='An identifying name for your keystore key',
    )
    KEY_ALIAS = cli.ArgumentProperties.duplicate(
        KEY_ALIAS_OPTIONAL,
        argparse_kwargs={'required': True},
    )
    KEY_PASSWORD = cli.ArgumentProperties(
        key='key_password',
        flags=('-l', '--ks-key-pass', '--key-pass'),
        type=argument_types.KeyPassword,
        description=(
            'Secure password for your keystore key. '
            f'Keystore password specified by {Colors.BRIGHT_BLUE("--keystore-pass")} '
            f'will be used in case it is not given.'
        ),
        argparse_kwargs={
            'required': False,
            'default': None,
        },
    )
    JSON_OUTPUT = cli.ArgumentProperties(
        key='json_output',
        flags=('--json',),
        type=bool,
        description='Whether to show the information in JSON format',
        argparse_kwargs={'required': False, 'action': 'store_true'},
    )


class CreateAndroidKeystoreArgument(cli.Argument):
    OVERWRITE_EXISTING = cli.ArgumentProperties(
        key='overwrite_existing',
        flags=('-o', '--overwrite-existing'),
        type=bool,
        description='Overwrite keystore at specified path in case it exists',
        argparse_kwargs={
            'required': False,
            'action': 'store_true',
        },
    )
    VALIDITY_DAYS = cli.ArgumentProperties(
        key='validity_days',
        flags=('--validity',),
        type=int,
        description='How long will the keystore be valid in days',
        argparse_kwargs={
            'required': False,
            'default': 10000,
        },
    )


class AndroidKeystoreIssuerArgument(cli.Argument):
    COMMON_NAME = cli.ArgumentProperties(
        key='issuer_common_name',
        flags=('-CN', '--common-name'),
        description='Common name of the keystore issuer. Either first and last name or company name',
        argparse_kwargs={'required': False},
    )
    ORGANIZATION = cli.ArgumentProperties(
        key='issuer_organization',
        flags=('-O', '--organization'),
        description='Organization of the keystore issuer',
        argparse_kwargs={'required': False},
    )
    ORGANIZATION_UNIT = cli.ArgumentProperties(
        key='issuer_organization_unit',
        flags=('-OU', '--organization-unit'),
        description=f'Organizational unit of the keystore issuer. For example `{Colors.WHITE("engineering")}`',
        argparse_kwargs={'required': False},
    )
    LOCALITY = cli.ArgumentProperties(
        key='issuer_locality',
        flags=('-L', '--locality'),
        description=(
            'Identifies the place where the keystore issuer resides. '
            'Locality can be a city, county, township, or other geographic region'
        ),
        argparse_kwargs={'required': False},
    )
    STATE_OR_PROVINCE = cli.ArgumentProperties(
        key='issuer_state_or_province',
        flags=('-ST', '--state'),
        description='Identifies the state or province in which the keystore issuer resides',
        argparse_kwargs={'required': False},
    )
    COUNTRY = cli.ArgumentProperties(
        key='issuer_country',
        flags=('-C', '--country'),
        type=argument_types.two_letter_country_code,
        description='Two-letter code of the country in which the keystore issuer resides',
        argparse_kwargs={'required': False},
    )
    DISTINGUISHED_NAME = cli.ArgumentProperties(
        key='issuer_distinguished_name',
        flags=('-DN', '--distinguished-name'),
        description=(
            'Instead of individually defining all keystore issuer attributes, it is possible to '
            'just define the distinguished name or the certificate that is included in the keystore. '
            'It should describe you or your company as the certificate issuer. '
            'If defined it takes precedence over individually set attributes. '
            f'For example `{Colors.WHITE("CN=corp.example.com,L=Mountain View,C=US")}`'
        ),
        argparse_kwargs={'required': False},
    )
