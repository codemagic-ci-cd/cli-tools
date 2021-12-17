from codemagic import cli


class AppStoreConnectActionGroup(cli.ActionGroup):
    APPS = cli.ActionGroupProperties(
        name='apps',
        description='Manage your apps in App Store Connect',
    )
    APP_STORE_VERSIONS = cli.ActionGroupProperties(
        name='app-store-versions',
        description='Manage the information related to an App Store version of your app',
    )
    APP_STORE_VERSION_LOCALIZATIONS = cli.ActionGroupProperties(
        name='app-store-version-localizations',
        description='Create and maintain version-specific App Store metadata that is localized.',
    )
    APP_STORE_VERSION_SUBMISSIONS = cli.ActionGroupProperties(
        name='app-store-version-submissions',
        description="Manage your application's App Store version review process",
    )
    BETA_APP_REVIEW_SUBMISSIONS = cli.ActionGroupProperties(
        name='beta-app-review-submissions',
        description="Manage your application's TestFlight submissions",
    )
    BUILDS = cli.ActionGroupProperties(
        name='builds',
        description='Manage your builds in App Store Connect',
    )
    BETA_BUILDS_LOCALIZATIONS = cli.ActionGroupProperties(
        name='beta-build-localizations',
        description='Manage your beta builds localizations in App Store Connect',
    )
    BETA_GROUPS = cli.ActionGroupProperties(
        name='beta-groups',
        description='Manage your groups of beta testers in App Store Connect',
    )
