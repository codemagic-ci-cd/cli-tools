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
        hasAccessToAllBuilds: Optional[bool] = None
        publicLinkEnabled: Optional[bool] = None
        publicLinkId: Optional[str] = None
        publicLinkLimitEnabled: Optional[bool] = None
        publicLinkLimit: Optional[int] = None
        publicLink: Optional[str] = None
        feedbackEnabled: Optional[bool] = None
        areIOSBuildsAvailableForAppleSiliconMac: Optional[bool] = None

    @dataclass
    class Relationships(Resource.Relationships):
        app: Relationship
        builds: Relationship
        betaTesters: Relationship
        betaBuildMetrics: Optional[Relationship] = None
