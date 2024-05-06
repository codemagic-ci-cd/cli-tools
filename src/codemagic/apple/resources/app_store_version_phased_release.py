from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .enums import PhasedReleaseState
from .resource import Resource


class AppStoreVersionPhasedRelease(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/appstoreversionphasedrelease
    """

    attributes: Resource.Attributes
    relationships: Optional[Relationships] = None

    @dataclass
    class Attributes(Resource.Attributes):
        currentDayNumber: int
        phasedReleaseState: PhasedReleaseState
        startDate: datetime
        totalPauseDuration: int

        def __post_init__(self):
            if isinstance(self.phasedReleaseState, str):
                self.phasedReleaseState = PhasedReleaseState(self.phasedReleaseState)
            if isinstance(self.startDate, str):
                self.startDate = Resource.from_iso_8601(self.startDate)

    @dataclass
    class Relationships(Resource.Relationships):
        pass
