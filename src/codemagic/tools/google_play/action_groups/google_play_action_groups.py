from codemagic import cli


class GooglePlayActionGroups(cli.ActionGroup):
    TRACKS = cli.ActionGroupProperties(
        name="tracks",
        description="Manage your Google Play release tracks",
    )
    APKS = cli.ActionGroupProperties(
        name="apks",
        description="Work with APKs in Google Play",
    )
    BUNDLES = cli.ActionGroupProperties(
        name="bundles",
        description="Work with App Bundles in Google Play",
    )
