from codemagic import cli
from codemagic.cli import Colors


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
