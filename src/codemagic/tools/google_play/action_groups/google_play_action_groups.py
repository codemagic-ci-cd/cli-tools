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
    DEOBFUSCATION_FILES = cli.ActionGroupProperties(
        name="deobfuscation-files",
        description="Manage APK deobfuscation files in Google Play",
    )
    EXPANSION_FILES = cli.ActionGroupProperties(
        name="expansion-files",
        description="Manage APK expansion files in Google Play",
    )
    INTERNAL_APP_SHARING = cli.ActionGroupProperties(
        name="internal-app-sharing",
        description="Share app bundles and APKs with your internal team using a Google Play link",
    )
