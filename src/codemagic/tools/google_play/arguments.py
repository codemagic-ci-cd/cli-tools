from codemagic import cli
from codemagic.cli import Colors
from codemagic.google.resources.google_play import DeobfuscationFileType
from codemagic.google.resources.google_play import ExpansionFileType
from codemagic.google.resources.google_play import Status

from . import argument_types

APPLICATION_BINARY_PATH_GROUP = cli.MutuallyExclusiveGroup(
    name="select application binary",
    required=True,
)
STAGED_ROLLOUT_AND_DRAFT_STATUS_GROUP = cli.MutuallyExclusiveGroup(
    name="configure publishing options",
    required=False,
)


class GooglePlayArgument(cli.Argument):
    GOOGLE_PLAY_SERVICE_ACCOUNT_CREDENTIALS = cli.ArgumentProperties(
        key="credentials",
        flags=("--credentials",),
        type=argument_types.CredentialsArgument,
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
            "choices": [s for s in Status if s is not Status.STATUS_UNSPECIFIED],
        },
    )
    PROMOTED_USER_FRACTION = cli.ArgumentProperties(
        key="promoted_user_fraction",
        flags=("--user-fraction",),
        type=cli.CommonArgumentTypes.bounded_number(float, 0, 1, inclusive=False),
        description=(
            "Fraction of users who are eligible for a staged promoted release in the target track. "
            f"Number from interval `{Colors.WHITE('0 < fraction < 1')}`. Can only be set when status is "
            f"`{Colors.WHITE(str(Status.IN_PROGRESS))}` or `{Colors.WHITE(str(Status.HALTED))}`."
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
            "choices": [s for s in Status if s is not Status.STATUS_UNSPECIFIED],
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
    APK_PATH_MUTUALLY_EXCLUSIVE = cli.ArgumentProperties.duplicate(
        APK_PATH,
        argparse_kwargs={"required": False},
        mutually_exclusive_group=APPLICATION_BINARY_PATH_GROUP,
    )
    APK_VERSION_CODE = cli.ArgumentProperties(
        key="apk_version_code",
        flags=("--version-code", "-c"),
        type=int,
        description="Version code of the APK file",
        argparse_kwargs={"required": True},
    )
    PROGUARD_MAPPING_PATH = cli.ArgumentProperties(
        key="proguard_mapping_path",
        flags=("--proguard-mapping",),
        type=cli.CommonArgumentTypes.existing_path,
        description="Path to the ProGuard mapping deobfuscation file to be uploaded for the published APK",
        argparse_kwargs={"required": False},
    )
    MAIN_EXPANSION_FILE_PATH = cli.ArgumentProperties(
        key="main_expansion_file_path",
        flags=("--main-expansion-file",),
        type=cli.CommonArgumentTypes.existing_path,
        description="Main expansion file to be uploaded for the published APK",
        argparse_kwargs={"required": False},
    )
    PATCH_EXPANSION_FILE_PATH = cli.ArgumentProperties(
        key="patch_expansion_file_path",
        flags=("--patch-expansion-file",),
        type=cli.CommonArgumentTypes.existing_path,
        description="Patch expansion file to be uploaded for the published APK",
        argparse_kwargs={"required": False},
    )


class BundlesArgument(cli.Argument):
    BUNDLE_PATH = cli.ArgumentProperties(
        key="bundle_path",
        flags=("--bundle", "-b"),
        type=cli.CommonArgumentTypes.existing_path,
        description="Path to App Bundle file (*.aab)",
        argparse_kwargs={"required": True},
    )
    BUNDLE_PATH_MUTUALLY_EXCLUSIVE = cli.ArgumentProperties.duplicate(
        BUNDLE_PATH,
        argparse_kwargs={"required": False},
        mutually_exclusive_group=APPLICATION_BINARY_PATH_GROUP,
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
        type=DeobfuscationFileType,
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


class ReleaseArgument(cli.Argument):
    RELEASE_NAME = cli.ArgumentProperties(
        key="release_name",
        flags=("--release-name", "-r"),
        description=(
            "Name of the release. Not required to be unique. If not set, "
            f"the name is generated from the APK's or App Bundles `{Colors.WHITE('versionName')}`"
        ),
        argparse_kwargs={"required": False},
    )
    IN_APP_UPDATE_PRIORITY = cli.ArgumentProperties(
        key="in_app_update_priority",
        flags=("--in-app-update-priority", "-i"),
        type=cli.CommonArgumentTypes.bounded_number(int, 0, 5, inclusive=True),
        description=(
            "Priority of the release. If your application supports in-app updates, "
            "set the release priority by specifying an integer in range [0, 5]"
        ),
        argparse_kwargs={"required": False},
    )
    STAGED_ROLLOUT_FRACTION = cli.ArgumentProperties(
        key="staged_rollout_fraction",
        flags=("--rollout-fraction", "-f"),
        type=cli.CommonArgumentTypes.bounded_number(float, 0, 1, inclusive=False),
        description=(
            "Staged rollout user fraction from range (0, 1). "
            "When you have a new version of your application that you want to gradually deploy, "
            'you may choose to release it as a "staged rollout" version. If you do this, '
            "Google Play automatically deploys it to the desired fraction of the app's users which you specify"
        ),
        argparse_kwargs={"required": False},
        mutually_exclusive_group=STAGED_ROLLOUT_AND_DRAFT_STATUS_GROUP,
    )
    SUBMIT_AS_DRAFT = cli.ArgumentProperties(
        key="submit_as_draft",
        flags=("--draft", "-d"),
        type=bool,
        description=(
            "Indicates that the artifacts generated in the build will be uploaded to Google Play as a draft release."
        ),
        argparse_kwargs={
            "required": False,
            "action": "store_true",
        },
        mutually_exclusive_group=STAGED_ROLLOUT_AND_DRAFT_STATUS_GROUP,
    )
    CHANGES_NOT_SENT_FOR_REVIEW = cli.ArgumentProperties(
        key="changes_not_sent_for_review",
        flags=("--changes-not-sent-for-review",),
        type=bool,
        description=(
            "Do not send changes for review. Indicates that the changes in this edit will not be reviewed "
            "until they are explicitly sent for review from the Google Play Console UI"
        ),
        argparse_kwargs={
            "required": False,
            "action": "store_true",
        },
    )
    VERSION_CODES = cli.ArgumentProperties(
        key="version_codes",
        flags=("--version-code", "-c"),
        description=(
            "Version codes of all APKs and App Bundles in the release. "
            "Must include version codes to retain from previous releases."
        ),
        argparse_kwargs={
            "required": True,
            "nargs": "+",
            "metavar": "version-code",
        },
    )
    RELEASE_NOTES = cli.ArgumentProperties(
        key="release_notes",
        flags=("--release-notes", "-n"),
        type=argument_types.ReleaseNotesArgument,
        description=(
            "Localised release notes as a JSON encoded list to let users know what's in your release. "
            f'For example, "{Colors.WHITE(argument_types.ReleaseNotesArgument.example_value)}"'
        ),
        argparse_kwargs={
            "required": False,
        },
    )
