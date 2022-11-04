import enum
from typing import NamedTuple


class ActionGroupProperties(NamedTuple):
    name: str
    description: str


# mypy yields a false-positive type error on enums with multiple inheritance
# https://github.com/python/mypy/issues/9319
class ActionGroup(ActionGroupProperties, enum.Enum):  # type: ignore
    ...
