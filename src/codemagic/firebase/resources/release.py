from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import timezone

from .abstract_resource import AbstractResource


@dataclass
class ReleaseResource(AbstractResource):
    """https://firebase.google.com/docs/reference/app-distribution/rest/v1/projects.apps.releases#ReleaseNotes
    """
    @dataclass
    class ReleaseNotes:
        text: str

    name: str
    releaseNotes: ReleaseNotes
    displayVersion: str
    buildVersion: int
    createTime: datetime
    firebaseConsoleUri: str
    testingUri: str
    binaryDownloadUri: str

    label: str = field(default='releases', init=False, repr=False)

    def __post_init__(self):
        if isinstance(self.createTime, str):
            self.createTime = datetime.fromisoformat(self.createTime.rstrip('Z')).replace(tzinfo=timezone.utc)
        if isinstance(self.buildVersion, str):
            self.buildVersion = int(self.buildVersion)
        if isinstance(self.releaseNotes, dict):
            self.releaseNotes = self.ReleaseNotes(self.releaseNotes['text'])
