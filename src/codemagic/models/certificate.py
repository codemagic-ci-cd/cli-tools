from __future__ import annotations

import pathlib
import re
from datetime import datetime
from datetime import timezone
from typing import AnyStr
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from OpenSSL import crypto
from OpenSSL.crypto import X509

from codemagic.mixins import RunningCliAppMixin
from codemagic.mixins import StringConverterMixin
from codemagic.utilities import log

from .certificate_p12_exporter import P12Exporter
from .json_serializable import JsonSerializable
from .private_key import PrivateKey


class Certificate(JsonSerializable, RunningCliAppMixin, StringConverterMixin):
    DEFAULT_LOCATION = pathlib.Path(pathlib.Path.home(), 'Library', 'MobileDevice', 'Certificates')

    def __init__(self, x509_certificate: X509):
        self.x509 = x509_certificate

    @classmethod
    def _get_x509_certificate(cls, buffer: AnyStr, buffer_type: int):
        try:
            return crypto.load_certificate(buffer_type, cls._bytes(buffer))
        except crypto.Error as crypto_error:
            format_name = {crypto.FILETYPE_PEM: 'PEM', crypto.FILETYPE_ASN1: 'ASN1'}[buffer_type]
            log.get_file_logger(cls).exception(f'Failed to initialize certificate: Invalid {format_name} contents')
            raise ValueError(f'Not a valid {format_name} certificate content') from crypto_error

    # Factory methods #

    @classmethod
    def from_pem(cls, pem: AnyStr) -> Certificate:
        x509_certificate = cls._get_x509_certificate(pem, crypto.FILETYPE_PEM)
        return Certificate(x509_certificate)

    @classmethod
    def from_ans1(cls, asn1: AnyStr) -> Certificate:
        x509_certificate = cls._get_x509_certificate(asn1, crypto.FILETYPE_ASN1)
        return Certificate(x509_certificate)

    @classmethod
    def from_p12(cls, p12: bytes, password: Optional[AnyStr] = None) -> Certificate:
        password_encoded = None if password is None else cls._bytes(password)
        p12_archive = crypto.load_pkcs12(p12, password_encoded)
        x509_certificate = p12_archive.get_certificate()
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
    def expires_at(self) -> datetime:
        naive_dt = datetime.strptime(self.not_after, '%Y%m%d%H%M%SZ')
        return naive_dt.astimezone(timezone.utc)

    @property
    def serial(self) -> int:
        return self.x509.get_serial_number()

    @property
    def extensions(self) -> List[str]:
        extensions_count = self.x509.get_extension_count()
        return [self._str(self.x509.get_extension(i).get_short_name()) for i in range(extensions_count)]

    @property
    def is_development_certificate(self) -> bool:
        development_certificate_pattern = re.compile(
            r'^((Apple Development)|(iPhone Developer)):.*$')
        return development_certificate_pattern.match(self.common_name) is not None

    def is_code_signing_certificate(self) -> bool:
        code_signing_certificate_patterns = (
            re.compile(r'^Apple (Development|Distribution):.*$'),
            re.compile(r'^iPhone (Developer|Distribution):.*$'),
            re.compile(r'^Developer ID Application:.*$'),
            re.compile(r'^Mac Developer:.*$'),
            re.compile(r'^3rd Party Mac Developer (Application|Installer):.*$'),
        )
        return any(p.match(self.common_name) is not None for p in code_signing_certificate_patterns)

    def dict(self) -> Dict[str, Union[str, int, Dict[str, str], List[str]]]:
        return {
            'common_name': self.common_name,
            'extensions': self.extensions,
            'has_expired': self.has_expired,
            'issuer': self.issuer,
            'is_development_certificate': self.is_development_certificate,
            'not_after': self.not_after,
            'not_before': self.not_before,
            'serial': self.serial,
            'subject': self.subject,
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

    def get_fingerprint(self, algorithm: hashes.HashAlgorithm) -> str:
        x509_certificate = self.x509.to_cryptography()
        fingerprint = x509_certificate.fingerprint(algorithm)
        return fingerprint.hex().upper()

    def export_p12(self,
                   private_key: PrivateKey,
                   container_password: str,
                   export_path: Optional[Union[pathlib.Path, AnyStr]] = None) -> pathlib.Path:
        """
        :raises: IOError, ValueError
        """
        if isinstance(export_path, (str, bytes)):
            _export_path: Optional[pathlib.Path] = pathlib.Path(self._str(export_path))
        else:
            _export_path = export_path

        exporter = P12Exporter(self, private_key, container_password)
        return exporter.export(_export_path)

    def is_signed_with(self, private_key: PrivateKey) -> bool:
        certificate_public_key = self.x509.to_cryptography().public_key()
        rsa_key_public_key = private_key.public_key
        certificate_public_numbers = certificate_public_key.public_numbers()
        rsa_key_public_numbers = rsa_key_public_key.public_numbers()
        return certificate_public_numbers == rsa_key_public_numbers
