from codemagic import cli


class AppStoreConnectActionGroup(cli.ActionGroup):
    APP_STORE_VERSION_SUBMISSIONS = cli.ActionGroupProperties(
        name='app-store-version-submissions',
        description="Manage your application's App Store version review process",
    )
