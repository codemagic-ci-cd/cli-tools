import enum
from typing import NamedTuple


class ActionGroupProperties(NamedTuple):
    name: str
    description: str


class ActionGroup(ActionGroupProperties, enum.Enum):
    ...
