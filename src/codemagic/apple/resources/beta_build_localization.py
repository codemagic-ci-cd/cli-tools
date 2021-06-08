from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .resource import Relationship
from .resource import Resource


class BetaBuildLocalization(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/betabuildlocalization
    """

    @dataclass
    class Attributes(Resource.Attributes):
        locale: str
        whatsNew: Optional[str] = None

    @dataclass
    class Relationships(Resource.Relationships):
        build: Relationship
