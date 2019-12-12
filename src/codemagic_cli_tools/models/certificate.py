import pathlib
import re
from pathlib import Path
from typing import AnyStr
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union

from OpenSSL import crypto
from OpenSSL.crypto import X509
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKeyWithSerialization

from codemagic_cli_tools.cli.cli_types import ObfuscationPattern
from .byte_str_converter import BytesStrConverter
from .json_serializable import JsonSerializable

CommandRunner = Callable[[Tuple[str, ...], Optional[Sequence[ObfuscationPattern]]], None]


class Certificate(JsonSerializable, BytesStrConverter):
    DEFAULT_LOCATION = Path.home() / Path('Library', 'MobileDevice', 'Certificates')

    def __init__(self, pem: str):
        self._pem = pem
        self._x509 = crypto.load_certificate(crypto.FILETYPE_PEM, pem.encode())

    @property
    def subject(self) -> Dict[str, str]:
        subject = self._x509.get_subject()
        return {self._str(k): self._str(v) for k, v in subject.get_components()}

    @property
    def issuer(self) -> Dict[str, str]:
        issuer = self._x509.get_issuer()
        return {self._str(k): self._str(v) for k, v in issuer.get_components()}

    @property
    def common_name(self) -> str:
        return self.subject['CN']

    @property
    def not_after(self) -> str:
        return self._str(self._x509.get_notAfter())

    @property
    def not_before(self) -> str:
        return self._str(self._x509.get_notBefore())

    @property
    def has_expired(self) -> bool:
        return self._x509.has_expired()

    @property
    def serial(self) -> int:
        return self._x509.get_serial_number()

    @property
    def extensions(self) -> List[str]:
        extensions_count = self._x509.get_extension_count()
        return [self._str(self._x509.get_extension(i).get_short_name()) for i in range(extensions_count)]

    def is_code_signing_certificate(self):
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

    @classmethod
    def create_certificate_signing_request(cls, rsa_key: RSAPrivateKey) -> x509.CertificateSigningRequest:
        subject_name = x509.Name([x509.NameAttribute(x509.NameOID.COMMON_NAME, 'PEM')])
        csr_builder = x509.CertificateSigningRequestBuilder() \
            .subject_name(subject_name)
        csr = csr_builder.sign(rsa_key, hashes.SHA256(), default_backend())
        return csr

    @classmethod
    def get_certificate_signing_request_content(cls, csr: x509.CertificateSigningRequest) -> str:
        public_bytes = csr.public_bytes(serialization.Encoding.PEM)
        return cls._str(public_bytes)

    @classmethod
    def asn1_to_x509(cls, asn1_certificate: AnyStr) -> X509:
        return crypto.load_certificate(crypto.FILETYPE_ASN1, cls._bytes(asn1_certificate))

    @classmethod
    def x509_to_pem(cls, x509_certificate: X509) -> str:
        pem = x509_certificate.to_cryptography().public_bytes(serialization.Encoding.PEM)
        return cls._str(pem)

    @classmethod
    def export_p12(cls,
                   x509_certificate: X509,
                   rsa_key: RSAPrivateKeyWithSerialization,
                   container_password: str,
                   export_path: Optional[pathlib.Path] = None,
                   command_runner: Optional[CommandRunner] = None) -> pathlib.Path:
        from .certificate_p12_exporter import P12Exporter
        exporter = P12Exporter(x509_certificate, rsa_key, container_password)
        return exporter.export(export_path, command_runner)

    @classmethod
    def is_signed_with_key(cls, x509_certificate: X509, rsa_key: RSAPrivateKey) -> bool:
        certificate_public_key = x509_certificate.to_cryptography().public_key()
        rsa_key_public_key = rsa_key.public_key()
        certificate_public_numbers = certificate_public_key.public_numbers()
        rsa_key_public_numbers = rsa_key_public_key.public_numbers()
        return certificate_public_numbers == rsa_key_public_numbers
