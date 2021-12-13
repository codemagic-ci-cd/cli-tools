from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .enums import Locale
from .resource import Relationship
from .resource import Resource


class AppStoreVersionLocalization(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/appstoreversionlocalization
    """

    @dataclass
    class Attributes(Resource.Attributes):
        description: str
        keywords: str
        locale: Locale
        marketingUrl: str
        promotionalText: str
        supportUrl: str
        whatsNew: str

        def __post_init__(self):
            if isinstance(self.locale, str):
                self.locale = Locale(self.locale)

    @dataclass
    class Relationships(Resource.Relationships):
        appPreviewSets: Optional[Relationship] = None
        appScreenshotSets: Optional[Relationship] = None
        appStoreVersion: Optional[Relationship] = None
