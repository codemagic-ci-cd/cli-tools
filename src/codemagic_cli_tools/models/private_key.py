from typing import Optional

from OpenSSL import crypto
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey


class PrivateKey:

    @classmethod
    def pem_to_rsa(cls, pem_key: bytes, password: Optional[bytes] = None) -> RSAPrivateKey:
        if password is None:
            password = b''
        pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, pem_key, password)
        return pkey.to_cryptography_key()

    @classmethod
    def get_public_key(cls, public_key: RSAPublicKey) -> bytes:
        return public_key.public_bytes(
            serialization.Encoding.OpenSSH,
            serialization.PublicFormat.OpenSSH
        )
