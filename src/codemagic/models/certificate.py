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
from cryptography.hazmat.primitives.serialization import pkcs12

from codemagic.cli import Colors
from codemagic.mixins import RunningCliAppMixin
from codemagic.mixins import StringConverterMixin
from codemagic.utilities import log

from .certificate_p12_exporter import P12Exporter
from .json_serializable import JsonSerializable
from .private_key import SUPPORTED_PUBLIC_KEY_TYPES
from .private_key import PrivateKey


class Certificate(JsonSerializable, RunningCliAppMixin, StringConverterMixin):
    DEFAULT_LOCATION = pathlib.Path(pathlib.Path.home(), 'Library', 'MobileDevice', 'Certificates')

    def __init__(self, certificate: x509.Certificate):
        if hasattr(certificate, 'to_cryptography'):
            # Legacy OpenSSL.crypto.X509 instance
            self._deprecation_warning()
            self.certificate = certificate.to_cryptography()  # type: ignore
        else:
            self.certificate = certificate

    @classmethod
    def _deprecation_warning(cls):
        cli_app = cls.get_current_cli_app()
        if cli_app is None:
            logger = log.get_logger(cls, log_to_stream=True)
        else:
            logger = cli_app.logger
        warning = (
            'WARNING! Creating `codemagic.models.Certificate` instances from '
            '`OpenSSL.crypto.X509` objects is deprecated and support for '
            'it will be removed in future versions. Use '
            '`cryptography.x509.Certificate` instances instead, or use factory methods.'
        )
        logger.warning(Colors.YELLOW(warning))

    # Factory methods #

    @classmethod
    def from_pem(cls, pem: AnyStr) -> Certificate:
        try:
            x509_certificate = x509.load_pem_x509_certificate(cls._bytes(pem))
        except ValueError as ve:
            log.get_file_logger(cls).exception('Failed to initialize certificate: Invalid PEM contents')
            raise ValueError('Not a valid PEM certificate content') from ve
        return Certificate(x509_certificate)

    @classmethod
    def from_ans1(cls, asn1: AnyStr) -> Certificate:
        try:
            x509_certificate = x509.load_der_x509_certificate(cls._bytes(asn1))
        except ValueError as ve:
            log.get_file_logger(cls).exception('Failed to initialize certificate: Invalid ASN1 contents')
            raise ValueError('Not a valid ASN1 certificate content') from ve
        return Certificate(x509_certificate)

    @classmethod
    def from_p12(cls, p12: bytes, password: Optional[AnyStr] = None) -> Certificate:
        password_encoded = None if password is None else cls._bytes(password)
        _, x509_certificate, _ = pkcs12.load_key_and_certificates(p12, password_encoded)
        if x509_certificate is None:
            raise ValueError('Certificate was not found from PKCS#12 container')
        return Certificate(x509_certificate)

    @property
    def subject(self) -> Dict[str, str]:
        return {
            self._get_rfc_4514_attribute_name(name_attribute): self._str(name_attribute.value)
            for name_attribute in self.certificate.subject
        }

    @property
    def issuer(self) -> Dict[str, str]:
        return {
            self._get_rfc_4514_attribute_name(name_attribute): self._str(name_attribute.value)
            for name_attribute in self.certificate.issuer
        }

    @property
    def common_name(self) -> str:
        return self.subject.get('CN', '')

    @property
    def not_after(self) -> str:
        """
        Get the timestamp at which the certificate stops being valid
        as an ASN.1 TIME YYYYMMDDhhmmssZ
        """
        not_after = self.certificate.not_valid_after
        return not_after.strftime('%Y%m%d%H%M%SZ')

    @property
    def not_before(self) -> str:
        not_before = self.certificate.not_valid_before
        return not_before.strftime('%Y%m%d%H%M%SZ')

    @property
    def has_expired(self) -> bool:
        current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
        return self.expires_at < current_time

    @property
    def expires_at(self) -> datetime:
        return self.certificate.not_valid_after.replace(tzinfo=timezone.utc)

    @property
    def serial(self) -> int:
        return self.certificate.serial_number

    @property
    def extensions(self) -> List[str]:
        return [self._str(e.oid._name) for e in self.certificate.extensions]

    @property
    def is_development_certificate(self) -> bool:
        development_certificate_pattern = re.compile(
            r'^((Apple Development)|(iPhone Developer)|(Mac Developer)):.*$',
        )
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
        pem = self.certificate.public_bytes(serialization.Encoding.PEM)
        return self._str(pem)

    @classmethod
    def create_certificate_signing_request(cls, private_key: PrivateKey) -> x509.CertificateSigningRequest:
        subject_name = x509.Name([x509.NameAttribute(x509.NameOID.COMMON_NAME, 'PEM')])
        csr_builder = x509.CertificateSigningRequestBuilder() \
            .subject_name(subject_name)
        csr = csr_builder.sign(private_key.cryptography_private_key, hashes.SHA256(), default_backend())
        return csr

    @classmethod
    def get_certificate_signing_request_content(cls, csr: x509.CertificateSigningRequest) -> str:
        public_bytes = csr.public_bytes(serialization.Encoding.PEM)
        return cls._str(public_bytes)

    def get_fingerprint(self, algorithm: hashes.HashAlgorithm) -> str:
        fingerprint = self.certificate.fingerprint(algorithm)
        return fingerprint.hex().upper()

    def export_p12(
        self,
        private_key: PrivateKey,
        container_password: str,
        export_path: Optional[Union[pathlib.Path, AnyStr]] = None,
    ) -> pathlib.Path:
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
        certificate_public_key = self.certificate.public_key()
        if not isinstance(certificate_public_key, SUPPORTED_PUBLIC_KEY_TYPES):
            raise TypeError('Public key type is not supported', type(certificate_public_key))
        certificate_public_numbers = certificate_public_key.public_numbers()
        private_key_public_numbers = private_key.public_key.public_numbers()
        return certificate_public_numbers == private_key_public_numbers

    def get_summary(self) -> Dict[str, Union[str, int, Dict[str, str]]]:
        return {
            'common_name': self.common_name,
            'serial_number': self.serial,
            'issuer': self.issuer,
            'expires_at': self.expires_at.isoformat(),
            'has_expired': self.has_expired,
            'sha1': self.get_fingerprint(hashes.SHA1()),
            'sha256': self.get_fingerprint(hashes.SHA256()),
        }

    def get_text_summary(self) -> str:
        issuer_name_transformation = {
            'CN': 'Common name',
            'OU': 'Organizational unit',
            'O': 'Organization',
            'L': 'Locality',
            'S': 'State or province',
            'ST': 'State',
            'C': 'Country',
        }
        return '\n'.join([
            '-- Certificate --',
            f'Common name: {self.common_name}',
            'Issuer:',
            *(f'    {issuer_name_transformation[k]}: {v}' for k, v in self.issuer.items()),
            f'Expires at: {self.expires_at}',
            f'Has expired: {self.has_expired}',
            f'Serial number: {self.serial}',
            f'SHA1: {self.get_fingerprint(hashes.SHA1())}',
            f'SHA256: {self.get_fingerprint(hashes.SHA256())}',
        ])

    @staticmethod
    def _get_rfc_4514_attribute_name(name_attribute: x509.NameAttribute) -> str:
        # Attribute rfc4514_attribute_name was introduced in cryptography version 35.0.0.
        # Use this if possible, otherwise resolve it from full RFC 4514 string which
        # also contains value.
        # https://cryptography.io/en/latest/x509/reference/#cryptography.509.NameAttribute.rfc4514_attribute_name
        if hasattr(name_attribute, 'rfc4514_attribute_name'):
            return name_attribute.rfc4514_attribute_name
        else:
            rfc4514_string = name_attribute.rfc4514_string()
            return rfc4514_string.split('=', maxsplit=1)[0]
