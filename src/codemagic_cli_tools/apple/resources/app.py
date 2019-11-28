from __future__ import annotations

from dataclasses import dataclass

from .resource import Relationship
from .resource import Resource


class App(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/app
    """

    @dataclass
    class Attributes(Resource.Attributes):
        name: str
        bundleId: str
        sku: str
        primaryLocale: str

    @dataclass
    class Relationships(Resource.Relationships):
        betaLicenseAgreement: Relationship
        preReleaseVersions: Relationship
        betaAppLocalizations: Relationship
        betaGroups: Relationship
        betaTesters: Relationship
        builds: Relationship
        betaAppReviewDetail: Relationship
