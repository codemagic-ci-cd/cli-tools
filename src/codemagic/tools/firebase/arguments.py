from codemagic import cli
from codemagic.firebase.resource_managers.resource_manager import ResourceManager

from .argument_types import CredentialsArgument


class FirebaseArgument(cli.Argument):
    PROJECT_ID = cli.ArgumentProperties(
        key='project_id',
        flags=('--project-id', '-p'),
        description='Project ID in Firebase. For example `228333310124`',
        argparse_kwargs={'required': True},
    )
    FIREBASE_SERVICE_ACCOUNT_CREDENTIALS = cli.ArgumentProperties(
        key='credentials',
        flags=('--credentials',),
        type=CredentialsArgument,
        description='Firebase service account credentials with `JSON` key type to access Firebase API',
        argparse_kwargs={'required': False},
    )
    JSON_OUTPUT = cli.ArgumentProperties(
        key='json_output',
        flags=('--json', '-j'),
        type=bool,
        description='Whether to show the request response in JSON format',
        argparse_kwargs={'required': False, 'action': 'store_true'},
    )


class ResourcesArgument(cli.Argument):
    LIMIT = cli.ArgumentProperties(
        key='limit',
        flags=('--limit', '-l'),
        type=int,
        description='The number of resources to list',
        argparse_kwargs={'required': False, 'default': 25},
    )
    ORDER_BY = cli.ArgumentProperties(
        key='order_by',
        flags=('--order-by', '-o'),
        type=ResourceManager.OrderBy,
        description='Sort resources in the specified order',
        argparse_kwargs={'required': False, 'default': ResourceManager.OrderBy.create_time_desc},
    )


class ReleasesArgument(cli.Argument):
    APP_ID = cli.ArgumentProperties(
        key='app_id',
        flags=('--app-id', '-a'),
        description='Application ID in Firebase. For example `1:228333310124:ios:5e439e0d0231a788ac8f09`',
        argparse_kwargs={'required': True},
    )
