from __future__ import annotations

import pathlib
import re
from pathlib import Path
from typing import AnyStr
from typing import Dict
from typing import List
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union

from OpenSSL import crypto
from OpenSSL.crypto import X509
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization

from codemagic_cli_tools.mixins import StringConverterMixin
from .certificate_p12_exporter import P12Exporter
from .json_serializable import JsonSerializable
from .private_key import PrivateKey

if TYPE_CHECKING:
    from codemagic_cli_tools.cli import CliApp


class Certificate(JsonSerializable, StringConverterMixin):
    DEFAULT_LOCATION = Path.home() / Path('Library', 'MobileDevice', 'Certificates')

    def __init__(self, x509_certificate: X509):
        self.x509 = x509_certificate

    # Factory methods #

    @classmethod
    def from_pem(cls, pem: AnyStr) -> Certificate:
        x509_certificate = crypto.load_certificate(crypto.FILETYPE_PEM, cls._bytes(pem))
        return Certificate(x509_certificate)

    @classmethod
    def from_ans1(cls, asn1: AnyStr) -> Certificate:
        x509_certificate = crypto.load_certificate(crypto.FILETYPE_ASN1, cls._bytes(asn1))
        return Certificate(x509_certificate)

    @property
    def subject(self) -> Dict[str, str]:
        subject = self.x509.get_subject()
        return {self._str(k): self._str(v) for k, v in subject.get_components()}

    @property
    def issuer(self) -> Dict[str, str]:
        issuer = self.x509.get_issuer()
        return {self._str(k): self._str(v) for k, v in issuer.get_components()}

    @property
    def common_name(self) -> str:
        return self.subject['CN']

    @property
    def not_after(self) -> str:
        return self._str(self.x509.get_notAfter())

    @property
    def not_before(self) -> str:
        return self._str(self.x509.get_notBefore())

    @property
    def has_expired(self) -> bool:
        return self.x509.has_expired()

    @property
    def serial(self) -> int:
        return self.x509.get_serial_number()

    @property
    def extensions(self) -> List[str]:
        extensions_count = self.x509.get_extension_count()
        return [self._str(self.x509.get_extension(i).get_short_name()) for i in range(extensions_count)]

    def is_code_signing_certificate(self) -> bool:
        code_signing_certificate_pattern = re.compile(
            r'^((Apple (Development|Distribution))|(iPhone (Developer|Distribution))):.*$')
        return code_signing_certificate_pattern.match(self.common_name) is not None

    def dict(self) -> Dict[str, Union[str, int, Dict[str, str], List[str]]]:
        return {
            'serial': self.serial,
            'subject': self.subject,
            'issuer': self.issuer,
            'not_after': self.not_after,
            'not_before': self.not_before,
            'has_expired': self.has_expired,
            'extensions': self.extensions,
        }

    def as_pem(self) -> str:
        pem = self.x509.to_cryptography().public_bytes(serialization.Encoding.PEM)
        return self._str(pem)

    @classmethod
    def create_certificate_signing_request(cls, private_key: PrivateKey) -> x509.CertificateSigningRequest:
        subject_name = x509.Name([x509.NameAttribute(x509.NameOID.COMMON_NAME, 'PEM')])
        csr_builder = x509.CertificateSigningRequestBuilder() \
            .subject_name(subject_name)
        csr = csr_builder.sign(private_key.rsa_key, hashes.SHA256(), default_backend())
        return csr

    @classmethod
    def get_certificate_signing_request_content(cls, csr: x509.CertificateSigningRequest) -> str:
        public_bytes = csr.public_bytes(serialization.Encoding.PEM)
        return cls._str(public_bytes)

    def export_p12(self,
                   private_key: PrivateKey,
                   container_password: str,
                   export_path: Optional[pathlib.Path] = None,
                   *,
                   cli_app: Optional['CliApp'] = None) -> pathlib.Path:
        """
        :raises: IOError, ValueError
        """
        exporter = P12Exporter(self, private_key, container_password)
        return exporter.export(export_path, cli_app=cli_app)

    def is_signed_with(self, private_key: PrivateKey) -> bool:
        certificate_public_key = self.x509.to_cryptography().public_key()
        rsa_key_public_key = private_key.public_key
        certificate_public_numbers = certificate_public_key.public_numbers()
        rsa_key_public_numbers = rsa_key_public_key.public_numbers()
        return certificate_public_numbers == rsa_key_public_numbers
