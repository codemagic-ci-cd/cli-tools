from __future__ import annotations

import dataclasses
import sys
from functools import wraps
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional
from typing import TypeVar

from .colors import Colors

if TYPE_CHECKING:
    from .action_group import ActionGroup
    from .argument import Argument
    from .cli_app import CliApp


_Fn = TypeVar("_Fn", bound=Callable[..., object])


@dataclasses.dataclass(frozen=True)
class ActionDeprecationInfo:
    alias: str
    version: str

    def get_message(self, replacement_action_name: str, *colors: Colors) -> str:
        executable_name, _ = replacement_action_name.split(maxsplit=1)
        deprecated_action_name = f"{executable_name} {self.alias}"
        deprecation_message = (
            f"Action `{deprecated_action_name}` was deprecated in version {self.version} "
            f"and replaced by equivalent action `{replacement_action_name}`.\n"
            f"Use `{replacement_action_name}` instead as `{deprecated_action_name}` "
            f"is subject for removal in future releases."
        )
        return Colors.apply(deprecation_message, *colors)


def action(
    action_name: str,
    *arguments: Argument,
    action_group: Optional[ActionGroup] = None,
    action_options: Optional[Dict[str, Any]] = None,
    deprecation_info: Optional[ActionDeprecationInfo] = None,
    suppress_help: bool = False,
) -> Callable[[_Fn], _Fn]:
    """
    Decorator to mark that the method is usable from CLI
    :param action_name: Name of the CLI parameter
    :param arguments: CLI arguments that are required for this method to work
    :param action_group: CLI argument group under which this action belongs
    :param action_options: Meta information about the action to check whether some conditions are met
    :param deprecation_info: Name and version pair describing the deprecated name of the action for
                             backwards compatibility, and in which version it was deprecated.
                             The action is registered on the root arguments parser with this name
                             without explicit documentation.
    :param suppress_help: Whether to suppress action info in help messages
    """

    # Ensure that each argument is used exactly once
    unique_arguments = set()
    function_cli_arguments = []
    for argument in arguments:
        argument_name = f"{argument.__class__.__name__}.{argument.name}"
        if argument_name not in unique_arguments:
            function_cli_arguments.append(argument)
            unique_arguments.add(argument_name)

    def decorator(func):
        if func.__doc__ is None:
            raise RuntimeError(f'Action "{action_name}" defined by {func} is not documented')
        func.action_group = action_group
        func.action_name = action_name
        func.arguments = function_cli_arguments
        func.is_cli_action = True
        func.deprecation_info = deprecation_info
        func.action_options = action_options or {}
        func.suppress_help = suppress_help

        @wraps(func)
        def wrapper(self: CliApp, *args, **kwargs):
            if deprecation_info and deprecation_info.alias in sys.argv:
                _notify_deprecated_action_usage(self, action_name, action_group, deprecation_info)
            return func(self, *args, **kwargs)

        return wrapper

    return decorator


def _notify_deprecated_action_usage(
    cli_app: CliApp,
    action_name: str,
    action_group: Optional[ActionGroup],
    deprecation_info: ActionDeprecationInfo,
):
    executable = cli_app.get_executable_name()
    name_parts = (executable, action_group.name if action_group else None, action_name)
    full_action_name = " ".join(p for p in name_parts if p)
    cli_app.echo(deprecation_info.get_message(full_action_name, Colors.YELLOW, Colors.BOLD))
