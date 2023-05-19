from abc import ABC
from dataclasses import dataclass


@dataclass
class AbstractFirebaseResource(ABC):
    label: str
