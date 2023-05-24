from dataclasses import dataclass
from typing import cast

from codemagic.firebase.resource_managers.resource_manager import ParentResourceIdentifier
from codemagic.firebase.resource_managers.resource_manager import PListableInterface
from codemagic.firebase.resource_managers.resource_manager import ResourceManager
from codemagic.firebase.resources import Release


class ProjectId(str):
    pass


class AppId(str):
    pass


@dataclass
class ReleaseParentIdentifier(ParentResourceIdentifier):
    project_id: ProjectId
    app_id: AppId

    @property
    def uri(self) -> str:
        return f'projects/{self.project_id}/apps/{self.app_id}'


class FirebaseReleaseManager(ResourceManager[Release, ReleaseParentIdentifier]):
    """
    https://firebase.google.com/docs/reference/app-distribution/rest/v1/projects.apps.releases/list
    """
    resource_type = Release

    @property
    def _discovery_interface(self) -> PListableInterface:
        discovery_interface = self._discovery_service.projects().apps().releases()  # type: ignore
        return cast(PListableInterface, discovery_interface)
