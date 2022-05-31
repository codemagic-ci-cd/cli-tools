from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .resource import Relationship
from .resource import Resource


class BetaAppReviewDetail(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/betaapplocalization
    """

    attributes: Attributes
    relationships: Optional[Relationships] = None

    @dataclass
    class Attributes(Resource.Attributes):
        contactEmail: Optional[str]
        contactFirstName: Optional[str]
        contactLastName: Optional[str]
        contactPhone: Optional[str]
        demoAccountName: Optional[str]
        demoAccountPassword: Optional[str]
        demoAccountRequired: bool
        notes: Optional[str]

    @dataclass
    class Relationships(Resource.Relationships):
        app: Relationship
