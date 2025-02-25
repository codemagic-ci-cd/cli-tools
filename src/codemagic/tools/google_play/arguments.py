from codemagic import cli
from codemagic.cli import Colors
from codemagic.google.resources.google_play import DeobfuscationFileType
from codemagic.google.resources.google_play import ExpansionFileType
from codemagic.google.resources.google_play import Status
from codemagic.tools.google_play.argument_types import CredentialsArgument


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
    PACKAGE_NAME = cli.ArgumentProperties(
        key="package_name",
        flags=("--package-name", "-p"),
        type=cli.CommonArgumentTypes.non_empty_string,
        description=(
            f"Package name of the app in Google Play Console. For example `{Colors.WHITE('com.example.app')}`"
        ),
        argparse_kwargs={"required": True},
    )


class TracksArgument(cli.Argument):
    TRACK_NAME = cli.ArgumentProperties(
        key="track_name",
        flags=("--track", "-t"),
        type=cli.CommonArgumentTypes.non_empty_string,
        description=f"Release track name. For example `{Colors.WHITE('alpha')}` or `{Colors.WHITE('production')}`",
        argparse_kwargs={"required": True},
    )


class InternalAppSharingArgument(cli.Argument):
    INTERNAL_APP_SHARING = cli.ArgumentProperties(
        key="internal_app_sharing",
        flags=("--internal-app-sharing", "-i"),
        type=bool,
        description="Whether to upload an APK or Android App Bundle through internal app sharing",
        argparse_kwargs={
            "required": False,
            "action": "store_true",
        },
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
        type=Status,
        description="Status of the promoted release in the target track",
        argparse_kwargs={
            "required": False,
            "default": Status.COMPLETED,
            "choices": list(Status),
        },
    )
    PROMOTED_USER_FRACTION = cli.ArgumentProperties(
        key="promoted_user_fraction",
        flags=("--user-fraction",),
        type=cli.CommonArgumentTypes.bounded_number(float, 0, 1, inclusive=False),
        description=(
            "Fraction of users who are eligible for a staged promoted release in the target track. "
            f"Number from interval `{Colors.WHITE('0 < fraction < 1')}`. Can only be set when status is "
            f"`{Colors.WHITE(str(Status.IN_PROGRESS))}` or `{Colors.WHITE(str(Status.HALTED))}`"
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
        type=Status,
        description="Promote only a source track release with the specified status",
        argparse_kwargs={
            "required": False,
            "choices": list(Status),
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


class ApksArgument(cli.Argument):
    APK_PATH = cli.ArgumentProperties(
        key="apk_path",
        flags=("--apk", "-a"),
        type=cli.CommonArgumentTypes.existing_path,
        description="Path to APK file (*.apk)",
        argparse_kwargs={"required": True},
    )
    APK_VERSION_CODE = cli.ArgumentProperties(
        key="apk_version_code",
        flags=("--version-code", "-c"),
        type=int,
        description="Version code of the APK file",
        argparse_kwargs={"required": True},
    )


class BundlesArgument(cli.Argument):
    BUNDLE_PATH = cli.ArgumentProperties(
        key="bundle_path",
        flags=("--bundle", "-b"),
        type=cli.CommonArgumentTypes.existing_path,
        description="Path to App Bundle file (*.aab)",
        argparse_kwargs={"required": True},
    )


class DeobfuscationsArgument(cli.Argument):
    DEOBFUSCATION_FILE_PATH = cli.ArgumentProperties(
        key="deobfuscation_file_path",
        flags=("--deobfuscation-file", "-d"),
        type=cli.CommonArgumentTypes.existing_path,
        description="Path to deobfuscation file",
        argparse_kwargs={"required": True},
    )
    DEOBFUSCATION_FILE_TYPE = cli.ArgumentProperties(
        key="deobfuscation_file_type",
        flags=("--type", "-t"),
        type=ExpansionFileType,
        description="The type of APK deobfuscation file which is being updated",
        argparse_kwargs={
            "required": False,
            "default": DeobfuscationFileType.PROGUARD,
            "choices": [t for t in DeobfuscationFileType if t is not DeobfuscationFileType.UNSPECIFIED],
        },
    )


class ExpansionFileArgument(cli.Argument):
    EXPANSION_FILE_PATH = cli.ArgumentProperties(
        key="expansion_file_path",
        flags=("--expansion-file", "-e"),
        type=cli.CommonArgumentTypes.existing_path,
        description="Path to APK expansion file",
        argparse_kwargs={"required": True},
    )
    EXPANSION_FILE_TYPE = cli.ArgumentProperties(
        key="expansion_file_type",
        flags=("--type", "-t"),
        type=ExpansionFileType,
        description="The file type of the expansion file configuration which is being updated",
        argparse_kwargs={
            "required": False,
            "default": ExpansionFileType.MAIN,
            "choices": [t for t in ExpansionFileType if t is not ExpansionFileType.UNSPECIFIED],
        },
    )
    REFERENCES_APK_VERSION_CODE = cli.ArgumentProperties(
        key="references_apk_version_code",
        flags=("--reference-version", "-r"),
        type=int,
        description=(
            "Update an APK's expansion file to reference another APK's expansion file specified by this version code"
        ),
        argparse_kwargs={"required": True},
    )
