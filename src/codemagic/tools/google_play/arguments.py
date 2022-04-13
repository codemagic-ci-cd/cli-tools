from codemagic import cli

from .argument_types import CredentialsArgument
from .argument_types import PackageName


class GooglePlayArgument(cli.Argument):
    GCLOUD_SERVICE_ACCOUNT_CREDENTIALS = cli.ArgumentProperties(
        key='credentials',
        flags=('--credentials',),
        type=CredentialsArgument,
        description=(
            'Gcloud service account credentials with `JSON` key type '
            'to access Google Play Developer API'
        ),
        argparse_kwargs={'required': False},
    )
    JSON_OUTPUT = cli.ArgumentProperties(
        key='json_output',
        flags=('--json', '-j'),
        type=bool,
        description='Whether to show the request response in JSON format',
        argparse_kwargs={'required': False, 'action': 'store_true'},
    )


class TracksArgument(cli.Argument):
    PACKAGE_NAME = cli.ArgumentProperties(
        key='package_name',
        flags=('--package-name', '-p'),
        type=PackageName,
        description='Package name of the app in Google Play Console. For example `com.example.app`',
        argparse_kwargs={'required': True},
    )
    TRACK_NAME = cli.ArgumentProperties(
        key='track_name',
        flags=('--track', '-t'),
        description='Release track name. For example `alpha` or `production`',
        argparse_kwargs={'required': True},
    )


class LatestBuildNumberArgument(cli.Argument):
    TRACKS = cli.ArgumentProperties(
        key='tracks',
        flags=('--tracks', '-t'),
        description=(
            'Get the build number from the specified track(s). '
            'If not specified, the highest build number across all tracks is returned'
        ),
        argparse_kwargs={
            'required': False,
            'nargs': '+',
        },
    )
