from __future__ import annotations

from typing import NamedTuple, Dict

from .resource import Resource, Relationship


class App(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/app
    """

    class Attributes(NamedTuple):
        name: str
        bundleId: str
        sku: str
        primaryLocale: str

        @classmethod
        def from_api_response(cls, api_response: Dict) -> App.Attributes:
            attributes = api_response['attributes']
            return App.Attributes(**attributes)

        def dict(self) -> Dict:
            return self._asdict()

    class Relationships(NamedTuple):
        betaLicenseAgreement: Relationship
        preReleaseVersions: Relationship
        betaAppLocalizations: Relationship
        betaGroups: Relationship
        betaTesters: Relationship
        builds: Relationship
        betaAppReviewDetail: Relationship

        @classmethod
        def from_api_response(cls, api_response: Dict) -> App.Relationships:
            return Relationship.create_relationships(App.Relationships, api_response)

        def dict(self) -> Dict:
            return {field_name: getattr(self, field_name).dict() for field_name in self._fields}

    def __init__(self, api_response: Dict):
        super().__init__(api_response)
        self.attributes = App.Attributes.from_api_response(api_response)
        self.relationships = App.Relationships.from_api_response(api_response)
