from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import NamedTuple


@dataclass
class PaginateResult:
    data: List[Dict]
    included: List[Dict]


class KeyIdentifier(str):
    pass


class IssuerId(str):
    pass


class ApiKey(NamedTuple):
    identifier: KeyIdentifier
    issuer_id: IssuerId
    private_key: str
