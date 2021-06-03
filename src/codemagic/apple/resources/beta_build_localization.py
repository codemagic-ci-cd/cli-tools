from __future__ import annotations

from dataclasses import dataclass

from .resource import Relationship
from .resource import Resource


class BetaBuildLocalization(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/betaapplocalization
    """

    @dataclass
    class Attributes(Resource.Attributes):
        locale: str
        whatsNew: str

    @dataclass
    class Relationships(Resource.Relationships):
        build: Relationship
