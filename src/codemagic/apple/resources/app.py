from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .enums import ContentRightsDeclaration
from .enums import Locale
from .enums import SubscriptionStatusUrlVersion
from .resource import Relationship
from .resource import Resource


class App(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/app
    """

    attributes: Attributes
    relationships: Optional[Relationships] = None

    @dataclass
    class Attributes(Resource.Attributes):
        bundleId: str
        name: str
        primaryLocale: Locale
        sku: str
        contentRightsDeclaration: ContentRightsDeclaration
        isOrEverWasMadeForKids: bool

        subscriptionStatusUrl: Optional[str] = None
        subscriptionStatusUrlForSandbox: Optional[str] = None
        subscriptionStatusUrlVersion: Optional[SubscriptionStatusUrlVersion] = None
        subscriptionStatusUrlVersionForSandbox: Optional[SubscriptionStatusUrlVersion] = None

        def __post_init__(self):
            if isinstance(self.contentRightsDeclaration, str):
                self.contentRightsDeclaration = ContentRightsDeclaration(self.contentRightsDeclaration)
            if isinstance(self.primaryLocale, str):
                self.primaryLocale = Locale(self.primaryLocale)
            if isinstance(self.subscriptionStatusUrlVersion, str):
                self.subscriptionStatusUrlVersion = SubscriptionStatusUrlVersion(self.subscriptionStatusUrlVersion)
            if isinstance(self.subscriptionStatusUrlVersionForSandbox, str):
                self.subscriptionStatusUrlVersionForSandbox = SubscriptionStatusUrlVersion(
                    self.subscriptionStatusUrlVersionForSandbox,
                )

    @dataclass
    class Relationships(Resource.Relationships):
        _OMIT_IF_NONE_KEYS = (
            "alternativeDistributionKey",
            "analyticsReportRequests",
            "appAvailability",
            "appAvailabilityV2",
            "appClips",
            "appCustomProductPages",
            "appEvents",
            "appPricePoints",
            "appPriceSchedule",
            "appStoreVersionExperimentsV2",
            "betaTesters",
            "ciProduct",
            "customerReviews",
            "gameCenterDetail",
            "inAppPurchasesV2",
            "marketplaceSearchDetail",
            "perfPowerMetrics",
            "pricePoints",
            "promotedPurchases",
            "reviewSubmissions",
            "subscriptionGracePeriod",
            "subscriptionGroups",
        )

        appInfos: Relationship
        appStoreVersions: Relationship
        betaAppLocalizations: Relationship
        betaAppReviewDetail: Relationship
        betaGroups: Relationship
        betaLicenseAgreement: Relationship
        builds: Relationship
        endUserLicenseAgreement: Relationship
        gameCenterEnabledVersions: Relationship
        preReleaseVersions: Relationship

        alternativeDistributionKey: Optional[Relationship] = None
        analyticsReportRequests: Optional[Relationship] = None
        appAvailability: Optional[Relationship] = None
        appAvailabilityV2: Optional[Relationship] = None
        appClips: Optional[Relationship] = None
        appCustomProductPages: Optional[Relationship] = None
        appEvents: Optional[Relationship] = None
        appPricePoints: Optional[Relationship] = None
        appPriceSchedule: Optional[Relationship] = None
        appStoreVersionExperimentsV2: Optional[Relationship] = None
        betaTesters: Optional[Relationship] = None
        ciProduct: Optional[Relationship] = None
        customerReviews: Optional[Relationship] = None
        gameCenterDetail: Optional[Relationship] = None
        inAppPurchases: Optional[Relationship] = None
        inAppPurchasesV2: Optional[Relationship] = None
        marketplaceSearchDetail: Optional[Relationship] = None
        perfPowerMetrics: Optional[Relationship] = None
        preOrder: Optional[Relationship] = None
        pricePoints: Optional[Relationship] = None
        promotedPurchases: Optional[Relationship] = None
        reviewSubmissions: Optional[Relationship] = None
        subscriptionGracePeriod: Optional[Relationship] = None
        subscriptionGroups: Optional[Relationship] = None
