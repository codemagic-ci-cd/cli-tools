#!/usr/bin/env python3
from __future__ import annotations

from typing import Callable
from typing import Sequence
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .argument import Argument


class ActionCallable:
    is_cli_action: bool
    action_name: str
    arguments: Sequence[Argument]
    __name__: str
    __call__: Callable
