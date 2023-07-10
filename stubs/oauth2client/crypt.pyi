from typing import Any
from typing import Optional

from oauth2client import _helpers as _helpers
from oauth2client import _openssl_crypt as _openssl_crypt
from oauth2client import _pure_python_crypt as _pure_python_crypt
from oauth2client import _pycrypto_crypt as _pycrypto_crypt

RsaSigner: Any
RsaVerifier: Any
CLOCK_SKEW_SECS: int
AUTH_TOKEN_LIFETIME_SECS: int
MAX_TOKEN_LIFETIME_SECS: int
logger: Any

class AppIdentityError(Exception): ...

def _bad_pkcs12_key_as_pem(*args: Any, **kwargs: Any) -> None: ...

OpenSSLSigner = _openssl_crypt.OpenSSLSigner
OpenSSLVerifier = _openssl_crypt.OpenSSLVerifier
pkcs12_key_as_pem = _openssl_crypt.pkcs12_key_as_pem
pkcs12_key_as_pem = _bad_pkcs12_key_as_pem
PyCryptoSigner = _pycrypto_crypt.PyCryptoSigner
PyCryptoVerifier = _pycrypto_crypt.PyCryptoVerifier
Signer = OpenSSLSigner
Verifier = OpenSSLVerifier
# Signer = PyCryptoSigner
# Verifier = PyCryptoVerifier
# Signer = RsaSigner
# Verifier = RsaVerifier

def make_signed_jwt(signer: Any, payload: Any, key_id: Optional[Any] = ...): ...
def _verify_signature(message: Any, signature: Any, certs: Any) -> None: ...
def _check_audience(payload_dict: Any, audience: Any) -> None: ...
def _verify_time_range(payload_dict: Any) -> None: ...
def verify_signed_jwt_with_certs(jwt: Any, certs: Any, audience: Optional[Any] = ...): ...
