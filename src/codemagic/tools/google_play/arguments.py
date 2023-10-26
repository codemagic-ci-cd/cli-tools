from codemagic import cli
from codemagic.cli import Colors
from codemagic.google_play.resources import ReleaseStatus

from .argument_types import CredentialsArgument


class GooglePlayArgument(cli.Argument):
    GCLOUD_SERVICE_ACCOUNT_CREDENTIALS = cli.ArgumentProperties(
        key="credentials",
        flags=("--credentials",),
        type=CredentialsArgument,
        description="Gcloud service account credentials with the `JSON` key type to access Google Play Developer API",
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
        type=cli.CommonArgumentTypes.non_empty_string,
        description=(
            f"Package name of the app in Google Play Console. For example `{Colors.WHITE('com.example.app')}`"
        ),
        argparse_kwargs={"required": True},
    )
    TRACK_NAME = cli.ArgumentProperties(
        key="track_name",
        flags=("--track", "-t"),
        type=cli.CommonArgumentTypes.non_empty_string,
        description=f"Release track name. For example `{Colors.WHITE('alpha')}` or `{Colors.WHITE('production')}`",
        argparse_kwargs={"required": True},
    )


class PromoteArgument(cli.Argument):
    SOURCE_TRACK_NAME = cli.ArgumentProperties(
        key="source_track_name",
        flags=("--source-track",),
        type=cli.CommonArgumentTypes.non_empty_string,
        description=f"Name of the track from where releases are promoted. For example `{Colors.WHITE('internal')}`",
        argparse_kwargs={"required": True},
    )
    TARGET_TRACK_NAME = cli.ArgumentProperties(
        key="target_track_name",
        flags=("--target-track",),
        type=cli.CommonArgumentTypes.non_empty_string,
        description=f"Name of the track to which releases are promoted. For example `{Colors.WHITE('alpha')}`",
        argparse_kwargs={"required": True},
    )
    PROMOTED_STATUS = cli.ArgumentProperties(
        key="promoted_status",
        flags=("--release-status",),
        type=ReleaseStatus,
        description="Status of the promoted release in the target track",
        argparse_kwargs={
            "required": False,
            "default": ReleaseStatus.COMPLETED,
            "choices": list(ReleaseStatus),
        },
    )
    PROMOTED_USER_FRACTION = cli.ArgumentProperties(
        key="promoted_user_fraction",
        flags=("--user-fraction",),
        type=cli.CommonArgumentTypes.bounded_number(float, 0, 1, inclusive=False),
        description=(
            "Fraction of users who are eligible for a staged promoted release in the target track. "
            f"Number from interval `{Colors.WHITE('0 < fraction < 1')}`. Can only be set when status is "
            f"`{Colors.WHITE(str(ReleaseStatus.IN_PROGRESS))}` or `{Colors.WHITE(str(ReleaseStatus.HALTED))}`"
        ),
        argparse_kwargs={"required": False},
    )
    PROMOTE_VERSION_CODE = cli.ArgumentProperties(
        key="promote_version_code",
        flags=("--version-code-filter",),
        description="Promote only a source track release that contains the specified version code",
        argparse_kwargs={"required": False},
    )
    PROMOTE_STATUS = cli.ArgumentProperties(
        key="promote_status",
        flags=("--release-status-filter",),
        type=ReleaseStatus,
        description="Promote only a source track release with the specified status",
        argparse_kwargs={
            "required": False,
            "choices": list(ReleaseStatus),
        },
    )


class LatestBuildNumberArgument(cli.Argument):
    TRACKS = cli.ArgumentProperties(
        key="tracks",
        flags=("--tracks", "-t"),
        type=cli.CommonArgumentTypes.non_empty_string,
        description=(
            "Get the build number from the specified track(s). "
            "If not specified, the highest build number across all tracks is returned"
        ),
        argparse_kwargs={
            "required": False,
            "nargs": "+",
        },
    )
