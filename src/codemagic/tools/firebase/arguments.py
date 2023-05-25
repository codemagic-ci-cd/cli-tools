from codemagic import cli

from .argument_types import CredentialsArgument


class FirebaseArgument(cli.Argument):
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


class ReleasesArgument(cli.Argument):
    PROJECT_ID = cli.ArgumentProperties(
        key='project_id',
        flags=('--project-id', '-p'),
        description='Project ID in Firebase. For example `228333310124`',
        argparse_kwargs={'required': True},
    )
    APP_ID = cli.ArgumentProperties(
        key='app_id',
        flags=('--app-id', '-a'),
        description='Application ID in Firebase. For example `1:228333310124:ios:5e439e0d0231a788ac8f09`',
        argparse_kwargs={'required': True},
    )
