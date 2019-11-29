from __future__ import annotations

import abc
import enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codemagic_cli_tools.apple import AppStoreConnectApiClient


class ResourceManager(metaclass=abc.ABCMeta):
    class Ordering(enum.Enum):
        def as_param(self, reverse=False):
            return f'{"-" if reverse else ""}{self.value}'

    def __init__(self, client: AppStoreConnectApiClient):
        self.client = client
