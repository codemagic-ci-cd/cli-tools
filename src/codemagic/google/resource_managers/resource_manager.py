from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Generic
from typing import Type
from typing import TypeVar

from googleapiclient import discovery

from codemagic.utilities import log

from ..resources import Resource

ResourceT = TypeVar("ResourceT", bound=Resource)
GoogleResourceT = TypeVar("GoogleResourceT", bound=discovery.Resource)


class ResourceManager(Generic[ResourceT, GoogleResourceT], ABC):
    def __init__(self, google_resource: GoogleResourceT):
        self._google_resource = google_resource
        self._logger = log.get_file_logger(self.__class__)

    @property
    @abstractmethod
    def resource_type(self) -> Type[ResourceT]:
        ...
