from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .enums import AppStoreState
from .enums import Platform
from .enums import ReleaseType
from .resource import Relationship
from .resource import Resource


class AppStoreVersion(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/appstoreversion
    """

    attributes: Attributes
    relationships: Optional[Relationships] = None

    @dataclass
    class Attributes(Resource.Attributes):
        platform: Platform
        appStoreState: AppStoreState
        copyright: str
        earliestReleaseDate: datetime
        releaseType: ReleaseType
        usesIdfa: bool
        versionString: str
        createdDate: datetime
        downloadable: bool

        def __post_init__(self):
            if isinstance(self.platform, str):
                self.platform = Platform(self.platform)
            if isinstance(self.appStoreState, str):
                self.appStoreState = AppStoreState(self.appStoreState)
            if isinstance(self.earliestReleaseDate, str):
                self.earliestReleaseDate = Resource.from_iso_8601(self.earliestReleaseDate)
            if isinstance(self.releaseType, str):
                self.releaseType = ReleaseType(self.releaseType)
            if isinstance(self.createdDate, str):
                self.createdDate = Resource.from_iso_8601(self.createdDate)

    @dataclass
    class Relationships(Resource.Relationships):
        _OMIT_IF_NONE_KEYS = ('app', 'appVersionExperiments')

        ageRatingDeclaration: Relationship
        appStoreReviewDetail: Relationship
        appStoreVersionLocalizations: Relationship
        appStoreVersionPhasedRelease: Relationship
        appStoreVersionSubmission: Relationship
        build: Relationship
        idfaDeclaration: Relationship
        routingAppCoverage: Relationship

        app: Optional[Relationship] = None
        appClipDefaultExperience: Optional[Relationship] = None
        appStoreVersionExperiments: Optional[Relationship] = None
        appVersionExperiments: Optional[Relationship] = None
