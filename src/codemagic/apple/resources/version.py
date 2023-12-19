import dataclasses

from .resource import DictSerializable
from .resource import ResourceId


@dataclasses.dataclass(frozen=True)
class ResourceVersion:
    id: ResourceId
    version: str


@dataclasses.dataclass
class BuildVersionInfo(DictSerializable):
    buildId: ResourceId
    version: str
    buildNumber: str

    def __str__(self) -> str:
        lines = (
            f"Build Id: {self.buildId}",
            f"Version: {self.version}",
            f"Build number: {self.buildNumber}",
        )
        return "\n".join(lines)
