from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .enums import BuildProcessingState
from .resource import DictSerializable
from .resource import Relationship
from .resource import Resource


@dataclass
class ImageAsset(DictSerializable):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/imageasset
    """

    templateUrl: str
    height: int
    width: int


class Build(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/build
    """

    attributes: Attributes
    relationships: Optional[Relationships] = None

    @dataclass
    class Attributes(Resource.Attributes):
        expired: bool
        iconAssetToken: ImageAsset
        minOsVersion: str
        processingState: BuildProcessingState
        version: str
        usesNonExemptEncryption: bool
        uploadedDate: datetime
        expirationDate: datetime

        def __post_init__(self):
            if isinstance(self.processingState, str):
                self.processingState = BuildProcessingState(self.processingState)
            if isinstance(self.uploadedDate, str):
                self.uploadedDate = Resource.from_iso_8601(self.uploadedDate)
            if isinstance(self.expirationDate, str):
                self.expirationDate = Resource.from_iso_8601(self.expirationDate)
            if isinstance(self.iconAssetToken, dict):
                self.iconAssetToken = ImageAsset(**self.iconAssetToken)

    @dataclass
    class Relationships(Resource.Relationships):
        _OMIT_IF_NONE_KEYS = ('betaGroups', 'perfPowerMetrics', 'diagnosticSignatures')

        app: Relationship
        appEncryptionDeclaration: Relationship
        individualTesters: Relationship
        preReleaseVersion: Relationship
        betaBuildLocalizations: Relationship
        buildBetaDetail: Relationship
        betaAppReviewSubmission: Relationship
        appStoreVersion: Relationship
        icons: Relationship

        betaGroups: Optional[Relationship] = None
        perfPowerMetrics: Optional[Relationship] = None
        diagnosticSignatures: Optional[Relationship] = None
