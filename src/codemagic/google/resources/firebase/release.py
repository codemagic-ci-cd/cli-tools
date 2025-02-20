from __future__ import annotations

import dataclasses
from datetime import datetime
from datetime import timezone
from typing import Optional

from codemagic.google.resources import Resource

from .release_notes import ReleaseNotes


@dataclasses.dataclass
class Release(Resource):
    """
    https://firebase.google.com/docs/reference/app-distribution/rest/v1/projects.apps.releases#resource:-release
    """

    name: str
    displayVersion: str
    buildVersion: str
    createTime: datetime
    firebaseConsoleUri: str
    testingUri: str
    binaryDownloadUri: str
    releaseNotes: Optional[ReleaseNotes] = None

    def __post_init__(self):
        if isinstance(self.createTime, str):
            self.createTime = datetime.fromisoformat(self.createTime.rstrip("Z")).replace(tzinfo=timezone.utc)
        if isinstance(self.releaseNotes, dict):
            self.releaseNotes = ReleaseNotes(self.releaseNotes["text"])
