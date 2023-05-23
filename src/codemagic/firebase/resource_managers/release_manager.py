from dataclasses import dataclass
from typing import cast

from codemagic.firebase.resource_managers.resource_manager import ListableInterfaceProtocol
from codemagic.firebase.resource_managers.resource_manager import ParentResourceIdentifier
from codemagic.firebase.resource_managers.resource_manager import ResourceManager
from codemagic.firebase.resources import Release


@dataclass
class ReleaseParentIdentifier(ParentResourceIdentifier):
    project_id: str
    app_id: str

    @property
    def uri(self) -> str:
        return f'projects/{self.project_id}/apps/{self.app_id}'


class FirebaseReleaseManager(ResourceManager[Release, ReleaseParentIdentifier]):
    """
    https://firebase.google.com/docs/reference/app-distribution/rest/v1/projects.apps.releases/list
    """
    resource_type = Release

    @property
    def _discovery_interface(self) -> ListableInterfaceProtocol:
        discovery_interface = self._discovery_service.projects().apps().releases()  # type: ignore
        return cast(ListableInterfaceProtocol, discovery_interface)
