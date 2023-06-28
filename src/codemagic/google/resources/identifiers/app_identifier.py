from dataclasses import dataclass

from .resource_identifier import ResourceIdentifier


@dataclass
class AppIdentifier(ResourceIdentifier):
    project_id: str
    app_id: str

    @property
    def uri(self) -> str:
        return f"projects/{self.project_id}/apps/{self.app_id}"
