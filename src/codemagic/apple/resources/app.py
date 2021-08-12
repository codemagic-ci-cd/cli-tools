from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .enums import ContentRightsDeclaration
from .resource import Relationship
from .resource import Resource


class App(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/app
    """

    @dataclass
    class Attributes(Resource.Attributes):
        bundleId: str
        name: str
        primaryLocale: str
        sku: str
        availableInNewTerritories: bool
        contentRightsDeclaration: ContentRightsDeclaration
        isOrEverWasMadeForKids: bool

        def __post_init__(self):
            if isinstance(self.contentRightsDeclaration, str):
                self.contentRightsDeclaration = ContentRightsDeclaration(self.contentRightsDeclaration)

    @dataclass
    class Relationships(Resource.Relationships):
        _OMIT_IF_NONE_KEYS = ('betaTesters', 'perfPowerMetrics')

        appInfos: Relationship
        appStoreVersions: Relationship
        availableTerritories: Relationship
        betaAppLocalizations: Relationship
        betaAppReviewDetail: Relationship
        betaGroups: Relationship
        betaLicenseAgreement: Relationship
        builds: Relationship
        ciProduct: Relationship
        endUserLicenseAgreement: Relationship
        gameCenterEnabledVersions: Relationship
        inAppPurchases: Relationship
        preOrder: Relationship
        preReleaseVersions: Relationship
        prices: Relationship

        betaTesters: Optional[Relationship] = None
        perfPowerMetrics: Optional[Relationship] = None
