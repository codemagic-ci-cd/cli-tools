from codemagic import cli


class FirebaseActionGroups(cli.ActionGroup):
    RELEASES = cli.ActionGroupProperties(
        name="releases",
        description="Manage your Firebase application releases",
    )
