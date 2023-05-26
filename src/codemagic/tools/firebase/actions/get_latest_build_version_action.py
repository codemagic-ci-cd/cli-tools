from abc import ABCMeta

from codemagic import cli
from codemagic.firebase.api_error import FirebaseApiClientError
from codemagic.firebase.resources.identifiers import AppIdentifier

from ..arguments import ReleasesArgument
from ..errors import FirebaseError
from ..firebase_action import FirebaseAction


class GetLatestBuildVersionAction(FirebaseAction, metaclass=ABCMeta):
    @cli.action('get-latest-build-version', ReleasesArgument.APP_ID)
    def get_latest_build_version(self, app_id: str) -> int:
        """
        Get latest build version from Firebase API
        """
        app_identifier = AppIdentifier(self.project_id, app_id)
        try:
            releases = self.api_client.releases.list(app_identifier, limit=1)
        except FirebaseApiClientError as e:
            raise FirebaseError(str(e))
        if not releases:
            raise FirebaseError('No available releases')

        build_version = releases[0].buildVersion
        self.echo(str(build_version))
        return build_version
