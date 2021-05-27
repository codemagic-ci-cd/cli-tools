#!/usr/bin/env python3
from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Sequence

if TYPE_CHECKING:
    from ..action_group import ActionGroup
    from .argument import Argument


class ActionCallable:
    action_group: Optional[ActionGroup]
    action_name: str
    arguments: Sequence[Argument]
    is_cli_action: bool
    action_options: Dict[str, Any]
    __name__: str
    __call__: Callable
