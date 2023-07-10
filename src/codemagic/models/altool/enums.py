from __future__ import annotations

import enum
import pathlib
from typing import AnyStr
from typing import Union

from codemagic.mixins import StringConverterMixin
from codemagic.models.application_package import Ipa


class AuthenticationMethod(enum.Enum):
    JSON_WEB_TOKEN = "JSON_WEB_TOKEN"
    USERNAME_AND_EMAIL = "username"
    NONE = "none"


class PlatformType(StringConverterMixin, str, enum.Enum):
    APPLE_TV_OS = "appletvos"
    MAC_OS = "osx"
    IOS = "ios"

    @classmethod
    def from_path(cls, artifact_path: Union[pathlib.Path, AnyStr]) -> PlatformType:
        if isinstance(artifact_path, (bytes, str)):
            artifact_path = pathlib.Path(cls._str(artifact_path))

        if artifact_path.suffix == ".pkg":
            return PlatformType.MAC_OS
        elif artifact_path.suffix == ".ipa":
            if Ipa(artifact_path).is_for_tvos():
                return PlatformType.APPLE_TV_OS
            return PlatformType.IOS
        else:
            raise ValueError(f"Unknown artifact type from path {artifact_path}")
