from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .enums import Locale
from .resource import Relationship
from .resource import Resource


class BetaBuildLocalization(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/betabuildlocalization
    """

    @dataclass
    class Attributes(Resource.Attributes):
        locale: Locale
        whatsNew: Optional[str] = None

        def __post_init__(self):
            if isinstance(self.locale, str):
                self.locale = Locale(self.locale)

    @dataclass
    class Relationships(Resource.Relationships):
        build: Relationship
