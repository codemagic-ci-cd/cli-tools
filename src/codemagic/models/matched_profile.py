from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .provisioning_profile import ProvisioningProfile


@dataclass
class MatchedProfile:
    profile: 'ProvisioningProfile'
    bundle_id: str
    project_name: str
    target_name: str
    build_configuration: str

    def format(self):
        return (
            f' - Using profile "{self.profile.name}" [{self.profile.uuid}] '
            f'for target "{self.target_name}" [{self.build_configuration}] '
            f'from project "{self.project_name}"'
        )

    def sort_key(self):
        return f'{self.project_name} {self.target_name} {self.build_configuration}'
