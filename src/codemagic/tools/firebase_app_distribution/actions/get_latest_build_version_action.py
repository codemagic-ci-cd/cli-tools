from abc import ABC

from codemagic import cli
from codemagic.google.errors import GoogleError

from ..arguments import ReleasesArgument
from ..errors import FirebaseAppDistributionError
from ..firebase_app_distribution_action import FirebaseAppDistributionAction


class GetLatestBuildVersionAction(FirebaseAppDistributionAction, ABC):
    @cli.action(
        "get-latest-build-version",
        ReleasesArgument.APP_ID,
    )
    def get_latest_build_version(self, app_id: str, should_print: bool = True) -> str:
        """
        Get latest build version from Firebase
        """
        try:
            releases = self.client.releases.list(self.project_number, app_id, limit=1)
        except GoogleError as e:
            raise FirebaseAppDistributionError(str(e))
        if not releases:
            raise FirebaseAppDistributionError(f"No releases available for {app_id}")

        build_version = releases[0].buildVersion
        if should_print:
            self.echo(build_version)

        return build_version
