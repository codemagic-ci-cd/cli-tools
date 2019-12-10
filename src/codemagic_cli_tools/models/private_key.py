from typing import AnyStr
from typing import Optional

from OpenSSL import crypto
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKeyWithSerialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.primitives.serialization import KeySerializationEncryption

from .byte_str_converter import BytesStrConverter


class PrivateKey(BytesStrConverter):

    @classmethod
    def pem_to_rsa(cls, pem_key: AnyStr, password: Optional[AnyStr] = None) -> RSAPrivateKeyWithSerialization:
        if password is None:
            key_password = b''
        else:
            key_password = cls._bytes(password)
        rsa_key = crypto.load_privatekey(crypto.FILETYPE_PEM, cls._bytes(pem_key), key_password)
        return rsa_key.to_cryptography_key()

    @classmethod
    def rsa_to_pem(cls, rsa_key: RSAPrivateKeyWithSerialization, password: Optional[AnyStr] = None) -> str:
        key_format = serialization.PrivateFormat.TraditionalOpenSSL
        algorithm: KeySerializationEncryption = serialization.NoEncryption()
        if password is not None:
            key_format = serialization.PrivateFormat.PKCS8
            algorithm = serialization.BestAvailableEncryption(cls._bytes(password))
        pem = rsa_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=key_format,
            encryption_algorithm=algorithm
        )
        return cls._str(pem)

    @classmethod
    def get_public_key(cls, public_key: RSAPublicKey) -> bytes:
        return public_key.public_bytes(
            serialization.Encoding.OpenSSH,
            serialization.PublicFormat.OpenSSH
        )
