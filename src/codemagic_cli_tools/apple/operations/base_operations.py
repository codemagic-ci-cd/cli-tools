from __future__ import annotations

import abc
import enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apple import AppStoreConnectApiClient


class BaseOrdering(enum.Enum):
    def as_param(self, reverse=False):
        return f'{"-" if reverse else ""}{self.value}'


class BaseOperations(metaclass=abc.ABCMeta):

    def __init__(self, client: AppStoreConnectApiClient):
        self.client = client
