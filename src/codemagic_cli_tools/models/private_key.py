from typing import Optional

from OpenSSL import crypto
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey


class PrivateKey:

    @classmethod
    def pem_to_rsa(cls, pem_key: bytes, password: Optional[bytes] = None) -> RSAPrivateKey:
        if password is None:
            password = b''
        pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, pem_key, password)
        return pkey.to_cryptography_key()
