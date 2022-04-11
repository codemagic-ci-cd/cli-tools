from codemagic import cli


class GooglePlayActionGroups(cli.ActionGroup):
    TRACKS = cli.ActionGroupProperties(
        name='tracks',
        description='Manage your Google Play release tracks',
    )
