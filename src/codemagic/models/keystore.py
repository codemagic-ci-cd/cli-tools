import pathlib
from dataclasses import dataclass

from .certificate_attributes import CertificateAttributes


@dataclass
class Keystore:
    certificate_attributes: CertificateAttributes
    key_alias: str
    key_password: str
    store_password: str
    store_path: pathlib.Path
    validity: int = 10000  # Validity duration in days
