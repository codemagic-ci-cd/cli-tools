from abc import ABC

from codemagic import cli
from codemagic.google.errors import GoogleError
from codemagic.google.resources.identifiers import AppIdentifier

from ..arguments import ReleasesArgument
from ..errors import FirebaseAppDistributionError
from ..firebase_app_distribution_action import FirebaseAppDistributionAction


class GetLatestBuildVersionAction(FirebaseAppDistributionAction, ABC):
    @cli.action(
        "get-latest-build-version",
        ReleasesArgument.APP_ID,
    )
    def get_latest_build_version(self, app_id: str, should_print: bool = True) -> int:
        """
        Get latest build version from Firebase
        """
        app_identifier = AppIdentifier(self.project_id, app_id)
        try:
            releases = self.client.releases.list(app_identifier, limit=1)
        except GoogleError as e:
            raise FirebaseAppDistributionError(str(e))
        if not releases:
            raise FirebaseAppDistributionError(f"No releases available for {app_identifier.app_id}")

        build_version = releases[0].buildVersion
        self.echo(str(build_version)) if should_print else None
        return build_version
