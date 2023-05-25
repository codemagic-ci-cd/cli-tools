from abc import ABC
from abc import abstractmethod
from typing import TypeVar

ResourceIdentifierT = TypeVar('ResourceIdentifierT', bound='ResourceIdentifier')


class ResourceIdentifier(ABC):
    @property
    @abstractmethod
    def uri(self) -> str:
        raise NotImplementedError()
