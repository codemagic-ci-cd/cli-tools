from dataclasses import dataclass
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
        createdDate: str
        isInternalGroup: bool
        hasAccessToAllBuilds: Optional[bool]
        publicLinkEnabled: Optional[bool]
        publicLinkId: Optional[str]
        publicLinkLimitEnabled: Optional[bool]
        publicLinkLimit: Optional[int]
        publicLink: Optional[str]
        feedbackEnabled: Optional[bool]
        areIOSBuildsAvailableForAppleSiliconMac: Optional[bool] = None

    @dataclass
    class Relationships(Resource.Relationships):
        app: Relationship
        builds: Relationship
        betaTesters: Relationship
        betaBuildMetrics: Optional[Relationship] = None
