from __future__ import annotations

import enum
import pathlib


class AuthenticationMethod(enum.Enum):
    JSON_WEB_TOKEN = 'JSON_WEB_TOKEN'
    USERNAME_AND_EMAIL = 'username'
    NONE = 'none'


class PlatformType(enum.Enum):
    APPLE_TV_OS = 'appletvos'
    MAC_OS = 'osx'
    IOS = 'ios'

    @classmethod
    def from_path(cls, artifact_path: pathlib.Path) -> PlatformType:
        if artifact_path.suffix == '.pkg':
            return PlatformType.MAC_OS
        elif artifact_path.suffix == '.ipa':
            return PlatformType.IOS
        else:
            raise ValueError(f'Unknown artifact type from path {artifact_path}')
