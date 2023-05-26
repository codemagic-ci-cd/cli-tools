import json
from abc import ABCMeta
from typing import List

from codemagic import cli
from codemagic.firebase.api_error import FirebaseApiClientError
from codemagic.firebase.resources import Release
from codemagic.firebase.resources.identifiers import AppIdentifier

from ..arguments import FirebaseArgument
from ..arguments import ReleasesArgument
from ..errors import FirebaseError
from ..firebase_action import FirebaseAction
from .firebase_action_groups import FirebaseActionGroups


class ReleasesActionGroup(FirebaseAction, metaclass=ABCMeta):
    @cli.action(
        'list',
        ReleasesArgument.PROJECT_ID,
        ReleasesArgument.APP_ID,
        FirebaseArgument.JSON_OUTPUT,
        action_group=FirebaseActionGroups.RELEASES,
    )
    def list_releases(
        self,
        project_id: str,
        app_id: str,
        json_output: bool = False,
        should_print: bool = True,
    ) -> List[Release]:
        """
        List releases for the application from Firebase API
        """

        app_identifier = AppIdentifier(project_id, app_id)
        try:
            releases = self.api_client.releases.list(app_identifier)
        except FirebaseApiClientError as e:
            raise FirebaseError(str(e))

        if should_print:
            if json_output:
                self.echo(json.dumps([t.dict() for t in releases], indent=4))
            else:
                for release in releases:
                    self.echo(str(release))

        return releases
