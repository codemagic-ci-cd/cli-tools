from abc import ABCMeta

from codemagic import cli
from codemagic.firebase.resources.identifiers import AppIdentifier

from ..arguments import AppId
from ..arguments import ProjectId
from ..arguments import ReleasesArgument
from ..errors import FirebaseError
from .firebase_action import FirebaseAction


class GetLatestBuildVersionAction(FirebaseAction, metaclass=ABCMeta):
    @cli.action(
        'get-latest-build-version',
        ReleasesArgument.PROJECT_ID,
        ReleasesArgument.APP_ID,
    )
    def get_latest_build_version(
        self,
        project_id: ProjectId,
        app_id: AppId,
    ) -> int:
        """
        Get latest build version from Firebase API
        """
        app_identifier = AppIdentifier(project_id, app_id)
        releases = self.api_client.releases.list(app_identifier, limit=1)
        if not releases:
            raise FirebaseError('No available releases')

        build_version = releases[0].buildVersion
        self.echo(str(build_version))
        return build_version
