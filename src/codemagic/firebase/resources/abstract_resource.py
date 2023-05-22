from abc import ABC
from dataclasses import dataclass


@dataclass
class AbstractResource(ABC):
    label: str
