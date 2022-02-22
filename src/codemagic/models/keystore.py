import pathlib
from dataclasses import dataclass
from typing import Optional

from .certificate_attributes import CertificateAttributes


@dataclass
class Keystore:
    certificate_attributes: CertificateAttributes
    key_alias: str
    path: pathlib.Path
    store_password: str
    validity: int = 10000  # Validity duration in days
    key_password: Optional[str] = None  # Will be the same as store password if not defined

    def __post_init__(self):
        if self.key_password is None:
            self.key_password = self.store_password
