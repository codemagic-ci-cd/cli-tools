from __future__ import annotations

import argparse
import dataclasses
from typing import TYPE_CHECKING
from typing import Dict
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Type

from codemagic.cli.cli_help_formatter import CliHelpFormatter
from codemagic.cli.colors import Colors

from .argument_formatter import ArgumentFormatter
from .mutually_exclusive_groups import MutuallyExclusiveGroup
from .mutually_exclusive_groups import MutuallyExclusiveGroups

if TYPE_CHECKING:
    from argparse import _ArgumentGroup as ArgumentGroup
    from argparse import _SubParsersAction as SubParsersAction

    from codemagic.cli import Argument
    from codemagic.cli.argument import ActionCallable
    from codemagic.cli.cli_app import CliApp


@dataclasses.dataclass
class _ArgumentGroups:
    required: Optional[ArgumentGroup] = None
    optionals: Optional[ArgumentGroup] = None
    mutually_exclusive: Dict[MutuallyExclusiveGroup, ArgumentGroup] = dataclasses.field(default_factory=dict)
    custom: Dict[str, ArgumentGroup] = dataclasses.field(default_factory=dict)

    def register_arguments(self, arguments: Sequence[Argument]):
        argument_group: Optional[ArgumentGroup]
        for argument in arguments:
            if argument.argument_group_name:
                argument_group = self.custom[argument.argument_group_name]
            elif argument.mutually_exclusive_group:
                argument_group = self.mutually_exclusive[argument.mutually_exclusive_group]
            elif argument.is_required():
                argument_group = self.required
            else:
                argument_group = self.optionals

            if argument_group:
                argument.register(argument_group)


class ArgumentParserBuilder:
    def __init__(
        self,
        cli_app: Type[CliApp],
        cli_action: ActionCallable,
        parent_parser: SubParsersAction,
        for_deprecated_alias: bool = False,
    ):
        self._cli_app = cli_app
        self._cli_action = cli_action
        self._action_parser = self._create_action_parser(parent_parser, for_deprecated_alias)

    def _create_action_parser(self, parent_parser: SubParsersAction, for_deprecated_alias: bool):
        if for_deprecated_alias:
            if self._cli_action.deprecation_info is None:
                raise RuntimeError(f"Deprecated alias requested for {self._cli_action.action_name} without alias")

            deprecation_message = self._cli_action.deprecation_info.get_message(
                self._full_action_name,
                Colors.YELLOW,
                Colors.BOLD,
            )
            return parent_parser.add_parser(
                self._cli_action.deprecation_info.alias,
                formatter_class=CliHelpFormatter,
                description=f"{deprecation_message} {Colors.BOLD(self._cli_action.__doc__)}",
            )
        elif self._cli_action.suppress_help:
            return parent_parser.add_parser(
                self._cli_action.action_name,
                formatter_class=CliHelpFormatter,
                description=Colors.BOLD(self._cli_action.__doc__),
            )
        else:
            return parent_parser.add_parser(
                self._cli_action.action_name,
                formatter_class=CliHelpFormatter,
                description=Colors.BOLD(self._cli_action.__doc__),
                help=self._cli_action.__doc__,
            )

    @property
    def _full_action_name(self) -> str:
        executable = self._cli_app.get_executable_name()
        if self._cli_action.action_group:
            return f"{executable} {self._cli_action.action_group.name} {self._cli_action.action_name}"
        else:
            return f"{executable} {self._cli_action.action_name}"

    @classmethod
    def set_default_cli_options(cls, cli_options_parser):
        options_group = cli_options_parser.add_argument_group(Colors.UNDERLINE("Options"))
        options_group.add_argument(
            "--log-stream",
            type=str,
            default="stderr",
            choices=["stderr", "stdout"],
            help=f"Log output stream. {ArgumentFormatter.format_default_value('stderr')}",
        )
        options_group.add_argument(
            "--no-color",
            dest="no_color",
            action="store_true",
            help="Do not use ANSI colors to format terminal output",
        )
        options_group.add_argument(
            "--version",
            dest="show_version",
            action="store_true",
            help="Show tool version and exit",
        )
        options_group.add_argument(
            "-s",
            "--silent",
            dest="enable_logging",
            action="store_false",
            help="Disable log output for commands",
        )
        options_group.add_argument(
            "-v",
            "--verbose",
            dest="verbose",
            action="store_true",
            help="Enable verbose logging for commands",
        )

        options_group.set_defaults(
            enable_logging=True,
            no_color=False,
            show_version=False,
            verbose=False,
        )

    @staticmethod
    def _get_mutually_exclusive_group_texts(group: MutuallyExclusiveGroup, executable: str) -> Tuple[str, str]:
        if group.required:
            title_prefix, description_prefix, description_verb = "Required", "Exactly", "must"
        else:
            title_prefix, description_prefix, description_verb = "Optional", "Only", "can"

        title = f"{title_prefix} mutually exclusive arguments for {executable} to {Colors.BOLD(group.name)}"
        description = f"{description_prefix} one of those options {description_verb} be selected"
        return title, description

    def _setup_custom_argument_groups(self, group_names: Sequence[str], executable) -> Dict[str, ArgumentGroup]:
        argument_groups = {}
        for group_name in group_names:
            description = f"Optional arguments for {executable} to {Colors.BOLD(group_name)}"
            argument_group = self._action_parser.add_argument_group(Colors.UNDERLINE(description))
            argument_groups[group_name] = argument_group
        return argument_groups

    def _setup_mutually_exclusive_groups(
        self,
        mutually_exclusive_groups: Sequence[MutuallyExclusiveGroup],
        executable: str,
    ) -> Dict[MutuallyExclusiveGroup, ArgumentGroup]:
        argument_groups = {}
        for mutually_exclusive_group in mutually_exclusive_groups:
            title, description = self._get_mutually_exclusive_group_texts(mutually_exclusive_group, executable)
            argument_group = self._action_parser.add_argument_group(Colors.UNDERLINE(title), description)
            mutually_exclusive_argument_group = argument_group.add_mutually_exclusive_group(
                required=mutually_exclusive_group.required,
            )
            argument_groups[mutually_exclusive_group] = mutually_exclusive_argument_group
        return argument_groups

    def _setup_cli_app_options(self):
        executable = self._action_parser.prog.split()[0]

        mutually_exclusive_groups = MutuallyExclusiveGroups.from_argument_list(self._cli_app.CLASS_ARGUMENTS)

        argument_groups = _ArgumentGroups()

        required_args_title = Colors.UNDERLINE(f"Required arguments for {Colors.BOLD(executable)}")
        argument_groups.required = self._action_parser.add_argument_group(required_args_title)
        argument_groups.mutually_exclusive.update(
            self._setup_mutually_exclusive_groups(mutually_exclusive_groups.required, executable),
        )

        optional_args_title = Colors.UNDERLINE(f"Optional arguments for {Colors.BOLD(executable)}")
        argument_groups.optionals = self._action_parser.add_argument_group(optional_args_title)
        argument_groups.mutually_exclusive.update(
            self._setup_mutually_exclusive_groups(mutually_exclusive_groups.optional, executable),
        )

        argument_groups.register_arguments(self._cli_app.CLASS_ARGUMENTS)

    def _setup_cli_action_options(self):
        executable = f"command {self._cli_action.action_name}"
        mutually_exclusive_groups = MutuallyExclusiveGroups.from_argument_list(self._cli_action.arguments)

        argument_groups = _ArgumentGroups()

        required_args_title = f"Required arguments for command {Colors.BOLD(self._cli_action.action_name)}"
        argument_groups.required = self._action_parser.add_argument_group(Colors.UNDERLINE(required_args_title))
        argument_groups.mutually_exclusive.update(
            self._setup_mutually_exclusive_groups(mutually_exclusive_groups.required, executable),
        )

        optional_args_title = f"Optional arguments for command {Colors.BOLD(self._cli_action.action_name)}"
        argument_groups.optionals = self._action_parser.add_argument_group(Colors.UNDERLINE(optional_args_title))
        argument_groups.mutually_exclusive.update(
            self._setup_mutually_exclusive_groups(mutually_exclusive_groups.optional, executable),
        )

        custom_group_names = {a.argument_group_name for a in self._cli_action.arguments if a.argument_group_name}
        argument_groups.custom = self._setup_custom_argument_groups(sorted(custom_group_names), executable)

        argument_groups.register_arguments(self._cli_action.arguments)

    def build(self) -> argparse.ArgumentParser:
        self._setup_cli_app_options()
        self._setup_cli_action_options()
        self.set_default_cli_options(self._action_parser)
        return self._action_parser
