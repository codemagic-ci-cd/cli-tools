from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .enums import Platform
from .resource import Relationship
from .resource import Resource


class PreReleaseVersion(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/prereleaseversion
    """

    attributes: Attributes
    relationships: Optional[Relationships] = None

    @dataclass
    class Attributes(Resource.Attributes):
        platform: Platform
        version: str

        def __post_init__(self):
            if isinstance(self.platform, str):
                self.platform = Platform(self.platform)

    @dataclass
    class Relationships(Resource.Relationships):
        app: Relationship
        builds: Relationship
