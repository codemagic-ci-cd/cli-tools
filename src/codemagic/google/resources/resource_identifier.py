from abc import ABC
from abc import abstractmethod


class ResourceIdentifier(ABC):
    @property
    @abstractmethod
    def uri(self) -> str:
        raise NotImplementedError()
