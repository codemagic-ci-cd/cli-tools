from codemagic import cli


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
