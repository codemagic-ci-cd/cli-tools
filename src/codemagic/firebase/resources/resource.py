from abc import ABC
from dataclasses import dataclass
from typing import ClassVar


@dataclass
class Resource(ABC):
    label: ClassVar[str]
