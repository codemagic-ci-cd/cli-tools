from __future__ import annotations

import dataclasses
from typing import NamedTuple
from typing import Sequence

from .argument import Argument


class MutuallyExclusiveGroup(NamedTuple):
    name: str
    required: bool


@dataclasses.dataclass(frozen=True)
class MutuallyExclusiveGroups:
    required: Sequence[MutuallyExclusiveGroup]
    optional: Sequence[MutuallyExclusiveGroup]

    @classmethod
    def from_argument_list(cls, arguments: Sequence[Argument]) -> MutuallyExclusiveGroups:
        required_groups, optional_groups = set(), set()

        for argument in arguments:
            if not argument.mutually_exclusive_group:
                continue
            elif argument.mutually_exclusive_group.required:
                required_groups.add(argument.mutually_exclusive_group)
            else:
                optional_groups.add(argument.mutually_exclusive_group)

        return MutuallyExclusiveGroups(
            required=tuple(required_groups),
            optional=tuple(optional_groups),
        )
