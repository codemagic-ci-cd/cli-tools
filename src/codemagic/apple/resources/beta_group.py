from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .resource import Relationship
from .resource import Resource


class BetaGroup(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/betagroup
    """

    @dataclass
    class Attributes(Resource.Attributes):
        name: str
        createdDate: datetime
        isInternalGroup: bool
        hasAccessToAllBuilds: Optional[bool]
        publicLinkEnabled: Optional[bool]
        publicLinkId: Optional[str]
        publicLinkLimitEnabled: Optional[bool]
        publicLinkLimit: Optional[int]
        publicLink: Optional[str]
        feedbackEnabled: Optional[bool]
        areIOSBuildsAvailableForAppleSiliconMac: Optional[bool] = None

        def __post_init__(self):
            if isinstance(self.createdDate, str):
                self.createdDate = Resource.from_iso_8601(self.createdDate)

    @dataclass
    class Relationships(Resource.Relationships):
        app: Relationship
        builds: Relationship
        betaTesters: Relationship
        betaBuildMetrics: Optional[Relationship] = None
