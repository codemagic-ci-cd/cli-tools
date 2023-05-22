from dataclasses import dataclass

from codemagic.firebase.resource_managers.abstract_base_manager import AbstractParentIdentifier
from codemagic.firebase.resource_managers.abstract_base_manager import ResourceManager
from codemagic.firebase.resources import ReleaseResource


@dataclass
class ReleaseParentIdentifier(AbstractParentIdentifier):
    project_id: str
    app_id: str

    @property
    def uri(self):
        return f'projects/{self.project_id}/apps/{self.app_id}'


class FirebaseReleaseResourceManager(ResourceManager[ReleaseResource, ReleaseParentIdentifier]):
    """
    https://firebase.google.com/docs/reference/app-distribution/rest/v1/projects.apps.releases/list
    """
    Resource = ReleaseResource
    ParentIdentifier = ReleaseParentIdentifier

    @property
    def _resource(self):
        return self.service.projects().apps().releases()
