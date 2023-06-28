from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from typing import Optional

from .release_notes import ReleaseNotes
from .resource import Resource


@dataclass
class Release(Resource):
    """
    https://firebase.google.com/docs/reference/app-distribution/rest/v1/projects.apps.releases
    """

    name: str
    displayVersion: str
    buildVersion: int
    createTime: datetime
    firebaseConsoleUri: str
    testingUri: str
    binaryDownloadUri: str
    releaseNotes: Optional[ReleaseNotes] = None

    def __post_init__(self):
        if isinstance(self.createTime, str):
            self.createTime = datetime.fromisoformat(self.createTime.rstrip("Z")).replace(tzinfo=timezone.utc)
        if isinstance(self.buildVersion, str):
            self.buildVersion = int(self.buildVersion)
        if isinstance(self.releaseNotes, dict):
            self.releaseNotes = ReleaseNotes(self.releaseNotes["text"])
