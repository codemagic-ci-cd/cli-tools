from dataclasses import dataclass
from typing import Dict
from typing import List


@dataclass
class PaginateResult:
    data: List[Dict]
    included: List[Dict]


class KeyIdentifier(str):
    pass


class IssuerId(str):
    pass
