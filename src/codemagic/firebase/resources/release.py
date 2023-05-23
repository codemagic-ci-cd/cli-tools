from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import timezone
from typing import ClassVar

from .resource import Resource


@dataclass
class ReleaseNotes:
    """
    https://firebase.google.com/docs/reference/app-distribution/rest/v1/projects.apps.releases#ReleaseNotes
    """
    text: str


@dataclass
class Release(Resource):
    """
    https://firebase.google.com/docs/reference/app-distribution/rest/v1/projects.apps.releases
    """
    name: str
    releaseNotes: ReleaseNotes
    displayVersion: str
    buildVersion: int
    createTime: datetime
    firebaseConsoleUri: str
    testingUri: str
    binaryDownloadUri: str

    label: ClassVar[str] = field(default='releases', init=False, repr=False)

    def __post_init__(self):
        if isinstance(self.createTime, str):
            self.createTime = datetime.fromisoformat(self.createTime.rstrip('Z')).replace(tzinfo=timezone.utc)
        if isinstance(self.buildVersion, str):
            self.buildVersion = int(self.buildVersion)
        if isinstance(self.releaseNotes, dict):
            self.releaseNotes = ReleaseNotes(self.releaseNotes['text'])
