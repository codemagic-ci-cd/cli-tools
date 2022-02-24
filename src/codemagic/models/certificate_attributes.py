from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields
from typing import Iterable
from typing import Optional
from typing import Tuple


@dataclass
class CertificateAttributes:
    common_name: Optional[str] = field(default=None, metadata={'abbr': 'CN'})
    organizational_unit: Optional[str] = field(default=None, metadata={'abbr': 'OU'})
    organization: Optional[str] = field(default=None, metadata={'abbr': 'O'})
    locality: Optional[str] = field(default=None, metadata={'abbr': 'L'})
    state_or_province: Optional[str] = field(default=None, metadata={'abbr': 'S'})
    country: Optional[str] = field(default=None, metadata={'abbr': 'C'})

    @classmethod
    def from_distinguished_name(cls, distinguished_name: str) -> CertificateAttributes:
        """
        Convert distinguished name like
        "CN=Sample Cert, OU=R&D, O=Company Ltd., L=Dublin 4, S=Dublin, C=IE"
        name to CertificateAttributes
        """
        certificate_attributes = cls()
        for part in distinguished_name.split(','):
            if not part.strip():
                continue
            short_name, value = part.strip().split('=')
            for class_field in fields(cls):
                if class_field.metadata['abbr'] == short_name:
                    setattr(certificate_attributes, class_field.name, value)
                    break
            else:
                raise ValueError(f'Unknown attribute name {short_name!r} in certificate distinguished name')
        return certificate_attributes

    def is_valid(self) -> bool:
        """
        Verify that at least one attribute is specified
        """
        return bool(self.get_components())

    def get_components(self) -> Iterable[Tuple[str, str]]:
        """
        Returns the components of this name, as a sequence of 2-tuples.
        """
        components_table = tuple(
            (instance_field.metadata['abbr'], getattr(self, instance_field.name))
            for instance_field in fields(self)
        )
        return [(name, value) for name, value in components_table if value is not None]

    def get_distinguished_name(self) -> str:
        components = self.get_components()
        if not components:
            raise ValueError('At least one certificate attribute is required to be non-empty')
        return ','.join(f'{name}={value}' for name, value in components)
