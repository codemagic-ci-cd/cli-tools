from __future__ import annotations

import dataclasses
from datetime import datetime
from datetime import timezone
from typing import Optional
from typing import overload

from codemagic.google.resources import Resource

from .release_notes import ReleaseNotes


@dataclasses.dataclass
class Release(Resource):
    """
    https://firebase.google.com/docs/reference/app-distribution/rest/v1/projects.apps.releases#resource:-release
    """

    name: str
    createTime: datetime
    firebaseConsoleUri: str
    testingUri: str
    binaryDownloadUri: str
    buildVersion: str
    displayVersion: str = ""
    releaseNotes: Optional[ReleaseNotes] = None
    updateTime: Optional[datetime] = None
    expireTime: Optional[datetime] = None

    def __post_init__(self):
        self.createTime = self._parse_datetime(self.createTime)
        self.updateTime = self._parse_datetime(self.updateTime)
        self.expireTime = self._parse_datetime(self.expireTime)
        if isinstance(self.releaseNotes, dict):
            self.releaseNotes = ReleaseNotes(self.releaseNotes["text"])

    @classmethod
    @overload
    def _parse_datetime(cls, timestamp: str) -> datetime: ...

    @classmethod
    @overload
    def _parse_datetime(cls, timestamp: datetime) -> datetime: ...

    @classmethod
    @overload
    def _parse_datetime(cls, timestamp: None) -> None: ...

    @classmethod
    def _parse_datetime(cls, timestamp: str | datetime | None) -> datetime | None:
        if isinstance(timestamp, datetime):
            return timestamp
        elif isinstance(timestamp, str):
            return datetime.fromisoformat(timestamp.rstrip("Z")).replace(tzinfo=timezone.utc)
        return None
