import pathlib
from dataclasses import dataclass

from .certificate_attributes import CertificateAttributes


@dataclass
class Keystore:
    key_alias: str
    key_password: str
    store_password: str
    store_path: pathlib.Path
    certificate_attributes: CertificateAttributes = CertificateAttributes()
    validity: int = 10000  # Validity duration in days
