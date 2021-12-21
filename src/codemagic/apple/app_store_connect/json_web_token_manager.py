from datetime import datetime
from datetime import timedelta
from typing import Dict
from typing import Optional

import jwt

from codemagic.mixins import StringConverterMixin
from codemagic.utilities import log

from .type_declarations import IssuerId
from .type_declarations import KeyIdentifier


class JsonWebTokenManager(StringConverterMixin):
    """
    Helper class to generate JSON web tokens for App Store Connect API as per
    https://developer.apple.com/documentation/appstoreconnectapi/generating_tokens_for_api_requests
    """

    def __init__(
        self,
        key_identifier: KeyIdentifier,
        issuer_id: IssuerId,
        private_key: str,
        audience='appstoreconnect-v1',
        algorithm='ES256',

    ):
        self._logger = log.get_logger(self.__class__)
        # Authentication information used to generate JWT
        self._key_identifier = key_identifier
        self._issuer_id = issuer_id
        self._private_key = private_key
        # JWT properties
        self._algorithm = algorithm
        self._audience = audience
        # Internal cache
        self._jwt: Optional[str] = None
        self._jwt_expires: datetime = datetime.now()

    def get_jwt(self) -> str:
        if self._jwt and not self._is_token_expired():
            return self._jwt
        self._logger.debug('Generate new JWT for App Store Connect')
        token = jwt.encode(
            self._get_jwt_payload(),
            self._private_key,
            algorithm=self._algorithm,
            headers={'kid': self._key_identifier})
        self._jwt = self._str(token)
        return self._jwt

    def _is_token_expired(self) -> bool:
        delta = timedelta(seconds=30)
        return datetime.now() - delta > self._jwt_expires

    def _get_timestamp(self) -> int:
        now = datetime.now()
        delta = timedelta(minutes=19)
        dt = now + delta
        self._jwt_expires = dt
        return int(dt.timestamp())

    def _get_jwt_payload(self) -> Dict:
        return {
            'iss': self._issuer_id,
            'exp': self._get_timestamp(),
            'aud': self._audience,
        }
