from __future__ import annotations

from typing import AnyStr
from typing import Optional
from typing import Union

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.dsa import DSAPrivateKey
from cryptography.hazmat.primitives.asymmetric.dsa import DSAPublicKey
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.primitives.serialization import KeySerializationEncryption
from cryptography.hazmat.primitives.serialization import pkcs12

from codemagic.mixins import StringConverterMixin
from codemagic.utilities import log

SUPPORTED_PRIVATE_KEY_TYPES = (
    DSAPrivateKey,
    EllipticCurvePrivateKey,
    RSAPrivateKey,
)

CryptographyPrivateKey = Union[
    DSAPrivateKey,
    EllipticCurvePrivateKey,
    RSAPrivateKey,
]

SUPPORTED_PUBLIC_KEY_TYPES = (
    DSAPublicKey,
    EllipticCurvePublicKey,
    RSAPublicKey,
)

CryptographyPublicKey = Union[
    DSAPublicKey,
    EllipticCurvePublicKey,
    RSAPublicKey,
]


class PrivateKey(StringConverterMixin):

    def __init__(self, cryptography_private_key: CryptographyPrivateKey):
        self.cryptography_private_key = cryptography_private_key

    @classmethod
    def from_buffer(cls, buffer: AnyStr, password: Optional[AnyStr] = None) -> PrivateKey:
        try:
            return cls.from_openssh_key(buffer, password)
        except ValueError:
            # Probably not an OpenSSH private key, try to load as PEM
            return cls.from_pem(buffer, password)

    @classmethod
    def from_openssh_key(cls, buffer: AnyStr, password: Optional[AnyStr] = None) -> PrivateKey:
        cryptography_private_key = serialization.load_ssh_private_key(
            cls._bytes(buffer),
            cls._bytes(password) if password else b'',
            default_backend(),
        )
        if isinstance(cryptography_private_key, Ed25519PrivateKey):
            raise ValueError('Ed25519 private keys are not supported')
        return PrivateKey(cryptography_private_key)

    @classmethod
    def from_pem(cls, pem_key: AnyStr, password: Optional[AnyStr] = None) -> PrivateKey:
        _password: Optional[bytes] = cls._bytes(password) if password is not None else None

        try:
            cryptography_private_key = serialization.load_pem_private_key(cls._bytes(pem_key), _password)
        except ValueError as ve:
            if 'bad decrypt' in str(ve).lower():
                log.get_file_logger(cls).exception('Failed to initialize private key: Invalid password')
                raise ValueError('Invalid private key passphrase') from ve
            else:
                log.get_file_logger(cls).exception('Failed to initialize private key: Invalid PEM contents')
                raise ValueError('Invalid private key PEM content') from ve
        except TypeError as te:
            log.get_file_logger(cls).exception('Failed to initialize private key: Invalid password')
            raise ValueError('Invalid private key passphrase') from te

        if not isinstance(cryptography_private_key, SUPPORTED_PRIVATE_KEY_TYPES):
            raise TypeError('Private key type is not supported', type(cryptography_private_key))

        return PrivateKey(cryptography_private_key)

    @classmethod
    def from_p12(cls, p12: bytes, password: Optional[AnyStr] = None) -> PrivateKey:
        password_encoded = None if password is None else cls._bytes(password)
        cryptography_private_key, _, _ = pkcs12.load_key_and_certificates(p12, password_encoded)
        if cryptography_private_key is None:
            raise ValueError('Private key is missing from PKCS#12')
        elif not isinstance(cryptography_private_key, SUPPORTED_PRIVATE_KEY_TYPES):
            raise TypeError('Private key type is not supported', type(cryptography_private_key))
        return PrivateKey(cryptography_private_key)

    def as_pem(self, password: Optional[AnyStr] = None) -> str:
        key_format = serialization.PrivateFormat.TraditionalOpenSSL
        algorithm: KeySerializationEncryption = serialization.NoEncryption()
        if password is not None:
            key_format = serialization.PrivateFormat.PKCS8
            algorithm = serialization.BestAvailableEncryption(self._bytes(password))
        pem = self.cryptography_private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=key_format,
            encryption_algorithm=algorithm,
        )
        return self._str(pem)

    @property
    def public_key(self) -> CryptographyPublicKey:
        return self.cryptography_private_key.public_key()

    def get_public_key(self) -> bytes:
        return self.public_key.public_bytes(
            serialization.Encoding.OpenSSH,
            serialization.PublicFormat.OpenSSH,
        )
