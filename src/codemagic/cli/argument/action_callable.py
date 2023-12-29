#!/usr/bin/env python3
from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import Protocol

if TYPE_CHECKING:
    from typing import Any
    from typing import Callable
    from typing import Dict
    from typing import Optional
    from typing import Sequence

    from ..action import DeprecationActionInfo
    from ..action_group import ActionGroup
    from .argument import Argument


class ActionCallable(Protocol):
    action_group: Optional[ActionGroup]
    action_name: str
    arguments: Sequence[Argument]
    is_cli_action: bool
    action_options: Dict[str, Any]
    deprecation_info: Optional[DeprecationActionInfo]
    __name__: str
    __call__: Callable


class DeprecatedActionCallable(ActionCallable):
    deprecation_info: DeprecationActionInfo
