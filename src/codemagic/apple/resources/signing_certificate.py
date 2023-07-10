from __future__ import annotations

from base64 import b64decode
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from typing import List
from typing import Optional

from cryptography import x509

from .bundle_id import BundleIdPlatform
from .enums import CertificateType
from .resource import Relationship
from .resource import Resource


class SigningCertificate(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/certificate
    """

    attributes: Attributes
    relationships: Optional[Relationships] = None

    @dataclass
    class Attributes(Resource.Attributes):
        displayName: str
        expirationDate: datetime
        name: str
        platform: BundleIdPlatform
        serialNumber: str
        certificateType: CertificateType
        certificateContent: str = field(metadata={"hide": True})
        csrContent: Optional[str] = field(metadata={"hide": True})

        def __post_init__(self):
            if isinstance(self.expirationDate, str):
                self.expirationDate = Resource.from_iso_8601(self.expirationDate)
            if isinstance(self.platform, str):
                self.platform = BundleIdPlatform(self.platform)
            if isinstance(self.certificateType, str):
                self.certificateType = CertificateType(self.certificateType)

    @dataclass
    class Relationships(Resource.Relationships):
        _OMIT_IF_NONE_KEYS = ("passTypeId",)

        passTypeId: Optional[Relationship] = None

    def get_display_info(self) -> str:
        return f"{self.attributes.name} ({self.id})"

    @property
    def asn1_content(self) -> bytes:
        return b64decode(self.attributes.certificateContent)

    @property
    def _certificate(self) -> x509.Certificate:
        return x509.load_der_x509_certificate(self.asn1_content)

    @property
    def common_name(self) -> str:
        subject = self._certificate.subject

        common_names: List[x509.NameAttribute] = subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)
        common_name: Optional[x509.NameAttribute] = next(iter(common_names), None)
        if not common_name:
            return "N/A"

        return common_name.value.decode() if isinstance(common_name.value, bytes) else common_name.value

    def __str__(self):
        return f"{super().__str__()}\nCommon name: {self.common_name}"
