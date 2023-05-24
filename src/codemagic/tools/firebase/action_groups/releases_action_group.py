import json
from abc import ABCMeta
from typing import List

from codemagic import cli
from codemagic.firebase.resource_managers.release_manager import AppId
from codemagic.firebase.resource_managers.release_manager import ProjectId
from codemagic.firebase.resource_managers.release_manager import ReleaseParentIdentifier
from codemagic.firebase.resources import Release

from ..arguments import FirebaseArgument
from ..arguments import ReleasesArgument
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
        project_id: ProjectId,
        app_id: AppId,
        json_output: bool = False,
        should_print: bool = True,
    ) -> List[Release]:
        """
        List releases for the specified project and application from Firebase API
        """

        parent_identifier = ReleaseParentIdentifier(project_id, app_id)
        releases = self.api_client.releases.list(parent_identifier)

        if should_print:
            if json_output:
                self.echo(json.dumps([t.dict() for t in releases], indent=4))
            else:
                for release in releases:
                    self.echo(str(release))

        return releases
