from codemagic import cli
from codemagic.google_play.resources import ReleaseStatus

from .argument_types import CredentialsArgument
from .argument_types import PackageName


class GooglePlayArgument(cli.Argument):
    GCLOUD_SERVICE_ACCOUNT_CREDENTIALS = cli.ArgumentProperties(
        key="credentials",
        flags=("--credentials",),
        type=CredentialsArgument,
        description="Gcloud service account credentials with `JSON` key type to access Google Play Developer API",
        argparse_kwargs={"required": False},
    )
    JSON_OUTPUT = cli.ArgumentProperties(
        key="json_output",
        flags=("--json", "-j"),
        type=bool,
        description="Whether to show the request response in JSON format",
        argparse_kwargs={"required": False, "action": "store_true"},
    )


class TracksArgument(cli.Argument):
    PACKAGE_NAME = cli.ArgumentProperties(
        key="package_name",
        flags=("--package-name", "-p"),
        type=PackageName,
        description="Package name of the app in Google Play Console. For example `com.example.app`",
        argparse_kwargs={"required": True},
    )
    TRACK_NAME = cli.ArgumentProperties(
        key="track_name",
        flags=("--track", "-t"),
        description="Release track name. For example `alpha` or `production`",
        argparse_kwargs={"required": True},
    )

    SOURCE_TRACK_NAME = cli.ArgumentProperties(
        key="source_track_name",
        flags=("--source-track",),
        description="Name of the track from where releases are promoted from. For example `internal`",
        argparse_kwargs={"required": True},
    )
    TARGET_TRACK_NAME = cli.ArgumentProperties(
        key="target_track_name",
        flags=("--target-track",),
        description="Name of the track to where releases are promoted to. For example `alpha`",
        argparse_kwargs={"required": True},
    )
    TRACK_PROMOTED_RELEASE_STATUS = cli.ArgumentProperties(
        key="promoted_release_status",
        flags=("--promoted-release-status",),
        type=ReleaseStatus,
        description="Release status in a promoted track",
        argparse_kwargs={
            "required": False,
            "default": ReleaseStatus.COMPLETED,
            "choices": list(ReleaseStatus),
        },
    )


class LatestBuildNumberArgument(cli.Argument):
    TRACKS = cli.ArgumentProperties(
        key="tracks",
        flags=("--tracks", "-t"),
        description=(
            "Get the build number from the specified track(s). "
            "If not specified, the highest build number across all tracks is returned"
        ),
        argparse_kwargs={
            "required": False,
            "nargs": "+",
        },
    )
