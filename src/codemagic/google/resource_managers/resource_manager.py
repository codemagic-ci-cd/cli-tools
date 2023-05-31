from __future__ import annotations

import logging
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Generic
from typing import Type
from typing import TypeVar

from codemagic.models.enums import ResourceEnum
from codemagic.utilities import log

if TYPE_CHECKING:
    from googleapiclient._apis.firebaseappdistribution.v1.resources import FirebaseAppDistributionResource

    from ..resources.resource import Resource

ResourceT = TypeVar('ResourceT', bound='Resource')


class ResourceManager(Generic[ResourceT], ABC):
    class OrderBy(ResourceEnum):
        create_time_desc = 'createTimeDesc'
        create_time_asc = 'createTime'

    def __init__(self, firebase_app_distribution: FirebaseAppDistributionResource):
        self._firebase_app_distribution = firebase_app_distribution
        self._logger = log.get_file_logger(self.__class__)

    @property
    @abstractmethod
    def resource_type(self) -> Type[ResourceT]:
        ...

    @property
    def logger(self) -> logging.Logger:
        return self._logger
