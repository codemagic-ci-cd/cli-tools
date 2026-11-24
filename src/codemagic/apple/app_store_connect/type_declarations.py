from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Tuple
from typing import Union


@dataclass
class PaginateResult:
    data: List[Dict]
    included: List[Dict]


class KeyIdentifier(str):
    pass


class IssuerId(str):
    pass


# Seconds, either for both connect and read, or as a (connect, read) tuple
RequestTimeout = Union[float, Tuple[float, float]]


class ApiKey(NamedTuple):
    identifier: KeyIdentifier
    issuer_id: IssuerId
    private_key: str
