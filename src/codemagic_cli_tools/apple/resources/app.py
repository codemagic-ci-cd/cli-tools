from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .resource import AbstractRelationships
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
    class Relationships(AbstractRelationships):
        betaLicenseAgreement: Relationship
        preReleaseVersions: Relationship
        betaAppLocalizations: Relationship
        betaGroups: Relationship
        betaTesters: Relationship
        builds: Relationship
        betaAppReviewDetail: Relationship

    def __init__(self, api_response: Dict):
        super().__init__(api_response)
        self.attributes: App.Attributes = App.Attributes.from_api_response(api_response)
        self.relationships: App.Relationships = App.Relationships.from_api_response(api_response)
