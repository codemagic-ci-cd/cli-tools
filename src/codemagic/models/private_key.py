from __future__ import annotations

from typing import AnyStr
from typing import Optional

from OpenSSL import crypto
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKeyWithSerialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.primitives.serialization import KeySerializationEncryption

from codemagic.mixins import StringConverterMixin
from codemagic.utilities import log


class PrivateKey(StringConverterMixin):

    def __init__(self, rsa_key: RSAPrivateKeyWithSerialization):
        self.rsa_key = rsa_key

    @classmethod
    def _get_pkey(cls, buffer: AnyStr, passphrase: bytes):
        try:
            return crypto.load_privatekey(crypto.FILETYPE_PEM, cls._bytes(buffer), passphrase)
        except crypto.Error as crypto_error:
            file_logger = log.get_file_logger(cls)
            for reason in crypto_error.args[0]:
                if 'bad decrypt' in reason:
                    file_logger.exception('Failed to initialize private key: Invalid password')
                    raise ValueError('Invalid private key passphrase') from crypto_error
            file_logger.exception('Failed to initialize private key: Invalid PEM contents')
            raise ValueError('Invalid private key PEM content') from crypto_error

    @classmethod
    def from_pem(cls, pem_key: AnyStr, password: Optional[AnyStr] = None) -> PrivateKey:
        pkey = cls._get_pkey(pem_key, cls._bytes(password) if password else b'')
        return PrivateKey(pkey.to_cryptography_key())

    def as_pem(self, password: Optional[AnyStr] = None) -> str:
        key_format = serialization.PrivateFormat.TraditionalOpenSSL
        algorithm: KeySerializationEncryption = serialization.NoEncryption()
        if password is not None:
            key_format = serialization.PrivateFormat.PKCS8
            algorithm = serialization.BestAvailableEncryption(self._bytes(password))
        pem = self.rsa_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=key_format,
            encryption_algorithm=algorithm
        )
        return self._str(pem)

    @property
    def public_key(self) -> RSAPublicKey:
        return self.rsa_key.public_key()

    def get_public_key(self) -> bytes:
        return self.public_key.public_bytes(
            serialization.Encoding.OpenSSH,
            serialization.PublicFormat.OpenSSH
        )
