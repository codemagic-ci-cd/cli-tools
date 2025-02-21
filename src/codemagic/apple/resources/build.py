from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .enums import BuildAudienceType
from .enums import BuildProcessingState
from .resource import AppleDictSerializable
from .resource import Relationship
from .resource import Resource
from .resource import ResourceId


@dataclass
class BuildVersionInfo(AppleDictSerializable):
    buildId: ResourceId
    version: str
    buildNumber: str

    def __str__(self) -> str:
        lines = (
            f"Build Id: {self.buildId}",
            f"Version: {self.version}",
            f"Build number: {self.buildNumber}",
        )
        return "\n".join(lines)


@dataclass
class ImageAsset(AppleDictSerializable):
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
        buildAudienceType: BuildAudienceType

        computedMinMacOsVersion: Optional[str] = None
        lsMinimumSystemVersion: Optional[str] = None
        computedMinVisionOsVersion: Optional[str] = None

        def __post_init__(self):
            if isinstance(self.buildAudienceType, str):
                self.buildAudienceType = BuildAudienceType(self.buildAudienceType)
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
        _OMIT_IF_NONE_KEYS = ("betaGroups", "perfPowerMetrics", "diagnosticSignatures")

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
