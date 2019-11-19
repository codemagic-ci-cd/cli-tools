import re
from pathlib import Path
from typing import Dict, List, Union

from OpenSSL import crypto

from .json_serializable import JsonSerializable


class Certificate(JsonSerializable):

    DEFAULT_LOCATION = Path.home() / Path('Library', 'MobileDevice', 'Certificates')

    def __init__(self, pem: str):
        self._pem = pem
        self._x509 = crypto.load_certificate(crypto.FILETYPE_PEM, pem.encode())

    @property
    def subject(self) -> Dict[str, str]:
        subject = self._x509.get_subject()
        return {k.decode(): v.decode() for k, v in subject.get_components()}

    @property
    def issuer(self) -> Dict[str, str]:
        issuer = self._x509.get_issuer()
        return {k.decode(): v.decode() for k, v in issuer.get_components()}

    @property
    def common_name(self) -> str:
        return self.subject['CN']

    @property
    def not_after(self) -> str:
        return self._x509.get_notAfter().decode()

    @property
    def not_before(self) -> str:
        return self._x509.get_notBefore().decode()

    @property
    def has_expired(self) -> bool:
        return self._x509.has_expired()

    @property
    def serial(self) -> int:
        return self._x509.get_serial_number()

    @property
    def extensions(self) -> List[str]:
        extensions_count = self._x509.get_extension_count()
        return [self._x509.get_extension(i).get_short_name().decode() for i in range(extensions_count)]

    def is_code_signign_certificate(self):
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
