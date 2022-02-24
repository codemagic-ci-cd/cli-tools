from codemagic import cli
from codemagic.cli import Colors

from . import argument_types


class AndroidKeystoreArgument(cli.Argument):
    KEYSTORE_PATH = cli.ArgumentProperties(
        key='keystore_path',
        flags=('-k', '--ks', '--keystore'),
        type=argument_types.KeystorePath,
        description='Path where your keystore should be created or read from',
    )
    KEYSTORE_PASSWORD = cli.ArgumentProperties(
        key='keystore_password',
        flags=('-p', '--ks-pass', '--keystore-pass'),
        type=argument_types.KeystorePassword,
        description='Secure password for your keystore',
        argparse_kwargs={'required': True},
    )
    KEY_ALIAS = cli.ArgumentProperties(
        key='key_alias',
        flags=('-a', '--ks-key-alias', '--alias'),
        type=argument_types.KeyAlias,
        description='An identifying name for your keystore key',
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


class AndroidKeystoreIssuerArgument(cli.Argument):
    COMMON_NAME = cli.ArgumentProperties(
        key='issuer_common_name',
        flags=('-CN', '--common-name'),
        type=argument_types.CommonName,
        description='Common name of the keystore issuer. Either first and last name or company name',
        argparse_kwargs={'required': False},
    )
    ORGANIZATION = cli.ArgumentProperties(
        key='issuer_organization',
        flags=('-O', '--organization'),
        type=argument_types.Organization,
        description='Organization of the keystore issuer',
        argparse_kwargs={'required': False},
    )
    ORGANIZATION_UNIT = cli.ArgumentProperties(
        key='issuer_organization_unit',
        flags=('-OU', '--organization-unit'),
        type=argument_types.OrganizationUnit,
        description=f'Organizational unit of the keystore issuer. For example `{Colors.WHITE("engineering")}`',
        argparse_kwargs={'required': False},
    )
    LOCALITY = cli.ArgumentProperties(
        key='issuer_locality',
        flags=('-L', '--locality'),
        type=argument_types.Locality,
        description=(
            'Identifies the place where the keystore issuer resides. '
            'Locality can be a city, county, township, or other geographic region'
        ),
        argparse_kwargs={'required': False},
    )
    STATE_OR_PROVINCE = cli.ArgumentProperties(
        key='issuer_state_or_province',
        flags=('-ST', '--state'),
        type=argument_types.StateOrProvince,
        description='Identifies the state or province in which the keystore issuer resides',
        argparse_kwargs={'required': False},
    )
    COUNTRY = cli.ArgumentProperties(
        key='issuer_country',
        flags=('-C', '--country'),
        type=argument_types.Country,
        description='Two-letter code of the country in which the keystore issuer resides',
        argparse_kwargs={'required': False},
    )
    DISTINGUISHED_NAME = cli.ArgumentProperties(
        key='issuer_distinguished_name',
        flags=('-DN', '--distinguished-name'),
        type=argument_types.DistinguishedName,
        description=(
            'Instead of individually defining all keystore issuer attributes, it is possible to '
            'just define the distinguished name or the certificate that is included in the keystore. '
            'It should describe you or your company as the certificate issuer. '
            'If defined it takes precedence over individually set attributes. '
            f'For example `{Colors.WHITE("CN=corp.example.com,L=Mountain View,C=US")}`'
        ),
        argparse_kwargs={'required': False},
    )
