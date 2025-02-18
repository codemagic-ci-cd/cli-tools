from codemagic import cli

from .argument_types import CredentialsArgument


class GooglePlayArgument(cli.Argument):
    GOOGLE_PLAY_SERVICE_ACCOUNT_CREDENTIALS = cli.ArgumentProperties(
        key="credentials",
        flags=("--credentials",),
        type=CredentialsArgument,
        description="Google Play service account credentials with JSON key type to access Google Play API",
        argparse_kwargs={"required": False},
    )
    JSON_OUTPUT = cli.ArgumentProperties(
        key="json_output",
        flags=("--json", "-j"),
        type=bool,
        description="Whether to show the request response in JSON format",
        argparse_kwargs={"required": False, "action": "store_true"},
    )
