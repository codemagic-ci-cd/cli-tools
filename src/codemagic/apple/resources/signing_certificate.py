from __future__ import annotations

from base64 import b64decode
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from typing import Optional

from OpenSSL import crypto

from .bundle_id import BundleIdPlatform
from .enums import CertificateType
from .resource import Resource


class SigningCertificate(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/certificate
    """

    @dataclass
    class Attributes(Resource.Attributes):
        displayName: str
        expirationDate: datetime
        name: str
        platform: BundleIdPlatform
        serialNumber: str
        certificateType: CertificateType
        certificateContent: str = field(metadata={'hide': True})
        csrContent: Optional[str] = field(metadata={'hide': True})

        def __post_init__(self):
            if isinstance(self.expirationDate, str):
                self.expirationDate = Resource.from_iso_8601(self.expirationDate)
            if isinstance(self.platform, str):
                self.platform = BundleIdPlatform(self.platform)
            if isinstance(self.certificateType, str):
                self.certificateType = CertificateType(self.certificateType)

    def get_display_info(self) -> str:
        return f'{self.attributes.certificateType} certificate {self.attributes.serialNumber}'

    @property
    def asn1_content(self) -> bytes:
        return b64decode(self.attributes.certificateContent)

    @property
    def _certificate(self) -> crypto.X509:
        return crypto.load_certificate(crypto.FILETYPE_ASN1, self.asn1_content)

    @property
    def common_name(self) -> str:
        subject = self._certificate.get_subject()
        for key, value in subject.get_components():
            if key in (b'CN', 'CN'):
                return value.decode() if isinstance(value, bytes) else value
        return 'N/A'

    def __str__(self):
        return f'{super().__str__()}\nCommon name: {self.common_name}'
