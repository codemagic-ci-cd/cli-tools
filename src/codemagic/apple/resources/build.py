from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .enums import BuildProcessingState
from .resource import Resource
from .resource import DictSerializable


class Build(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/build
    """

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

    @dataclass
    class Relationships(Resource.Relationships):
        app: Relationship
        appEncryptionDeclaration: Relationship
        individualTesters: Relationship
        preReleaseVersion: Relationship
        betaBuildLocalizations: Relationship
        buildBetaDetail: Relationship
        betaAppReviewSubmission: Relationship
        appStoreVersion: Relationship
        icons: Relationship

        betaGroups: Relationship
        perfPowerMetrics: Relationship
        diagnosticSignatures: Relationship

@dataclass
class ImageAsset(DictSerializable):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/imageasset
    """

    templateUrl: str
    height: int
    width: int
