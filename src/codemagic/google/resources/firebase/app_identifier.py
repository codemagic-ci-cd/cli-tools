from dataclasses import dataclass


@dataclass
class AppIdentifier:
    project_id: str
    app_id: str

    @property
    def uri(self) -> str:
        return f"projects/{self.project_id}/apps/{self.app_id}"
