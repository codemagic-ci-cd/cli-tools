from __future__ import annotations

import enum
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any

from .bundle_id import BundleIdPlatform
from .resource import Resource


class CertificateType(enum.Enum):
    DEVELOPER_ID_APPLICATION = 'DEVELOPER_ID_APPLICATION'
    DEVELOPER_ID_KEXT = 'DEVELOPER_ID_KEXT'
    IOS_DEVELOPMENT = 'IOS_DEVELOPMENT'
    IOS_DISTRIBUTION = 'IOS_DISTRIBUTION'
    MAC_APP_DEVELOPMENT = 'MAC_APP_DEVELOPMENT'
    MAC_APP_DISTRIBUTION = 'MAC_APP_DISTRIBUTION'
    MAC_INSTALLER_DISTRIBUTION = 'MAC_INSTALLER_DISTRIBUTION'


class Certificate(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/certificate
    """

    @dataclass
    class Attributes(Resource.Attributes):
        certificateContent: str
        displayName: str
        expirationDate: datetime
        name: str
        platform: BundleIdPlatform
        serialNumber: str
        certificateType: CertificateType
        csrContent: Any  # Undocumented attribute

        def __post_init__(self):
            if isinstance(self.expirationDate, str):
                self.expirationDate = Resource.from_iso_8601(self.expirationDate)
            if isinstance(self.platform, str):
                self.platform = BundleIdPlatform(self.platform)
            if isinstance(self.certificateType, str):
                self.certificateType = CertificateType(self.certificateType)

    def __init__(self, api_response: Dict):
        super().__init__(api_response)
        self.attributes: Certificate.Attributes = Certificate.Attributes.from_api_response(api_response)
        self.relationships = None

    def dict(self) -> Dict:
        d = super().dict()
        del d['relationships']
        return d
