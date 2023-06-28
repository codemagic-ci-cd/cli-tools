from codemagic import cli
from codemagic.cli.colors import Colors
from codemagic.google.resources import OrderBy

from .argument_types import CredentialsArgument


class FirebaseArgument(cli.Argument):
    PROJECT_ID = cli.ArgumentProperties(
        key="project_id",
        flags=("--project-id", "-p"),
        description=f'Project ID in Firebase. For example `{Colors.WHITE("228333310124")}`',
        argparse_kwargs={"required": True},
    )
    FIREBASE_SERVICE_ACCOUNT_CREDENTIALS = cli.ArgumentProperties(
        key="credentials",
        flags=("--credentials", "-c"),
        type=CredentialsArgument,
        description="Firebase service account credentials with JSON key type to access Firebase",
        argparse_kwargs={"required": False},
    )
    JSON_OUTPUT = cli.ArgumentProperties(
        key="json_output",
        flags=("--json", "-j"),
        type=bool,
        description="Whether to show the request response in JSON format",
        argparse_kwargs={"required": False, "action": "store_true"},
    )


class ResourcesArgument(cli.Argument):
    LIMIT = cli.ArgumentProperties(
        key="limit",
        flags=("--limit", "-l"),
        type=int,
        description="The number of resources to list",
        argparse_kwargs={"required": False, "default": 25},
    )
    ORDER_BY = cli.ArgumentProperties(
        key="order_by",
        flags=("--order-by", "-o"),
        type=OrderBy,
        description="Sort resources in the specified order",
        argparse_kwargs={
            "required": False,
            "default": OrderBy.CREATE_TIME_DESC,
            "choices": list(OrderBy),
        },
    )


class ReleasesArgument(cli.Argument):
    APP_ID = cli.ArgumentProperties(
        key="app_id",
        flags=("--app-id", "-a"),
        description=(
            f"Application ID in Firebase. For example `{Colors.WHITE('1:228333310124:ios:5e439e0d0231a788ac8f09')}`"
        ),
        argparse_kwargs={"required": True},
    )
