from __future__ import annotations

import argparse
from typing import TYPE_CHECKING
from typing import Dict
from typing import Type

from codemagic.cli.cli_help_formatter import CliHelpFormatter
from codemagic.cli.colors import Colors

from .argument_formatter import ArgumentFormatter

if TYPE_CHECKING:
    from argparse import _ArgumentGroup as ArgumentGroup
    from argparse import _SubParsersAction as SubParsersAction

    from codemagic.cli.argument import ActionCallable
    from codemagic.cli.cli_app import CliApp


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
        self._required_arguments = self._action_parser.add_argument_group(
            Colors.UNDERLINE(f"Required arguments for command {Colors.BOLD(cli_action.action_name)}"),
        )
        self._optional_arguments = self._action_parser.add_argument_group(
            Colors.UNDERLINE(f"Optional arguments for command {Colors.BOLD(cli_action.action_name)}"),
        )
        self._custom_arguments_groups: Dict[str, ArgumentGroup] = {}

    def _create_action_parser(self, parent_parser: SubParsersAction, for_deprecated_alias: bool):
        if for_deprecated_alias:
            if self._cli_action.deprecated_alias is None:
                raise RuntimeError(f"Deprecated alias requested for {self._cli_action.action_name} without alias")
            deprecation_message = Colors.YELLOW(Colors.BOLD(f"Deprecated alias for `{self._full_action_name}`."))
            return parent_parser.add_parser(
                self._cli_action.deprecated_alias,
                formatter_class=CliHelpFormatter,
                description=f"{deprecation_message} {Colors.BOLD(self._cli_action.__doc__)}",
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
            help=f'Log output stream. {ArgumentFormatter.format_default_value("stderr")}',
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

    def _get_custom_argument_group(self, group_name) -> ArgumentGroup:
        try:
            argument_group = self._custom_arguments_groups[group_name]
        except KeyError:
            group_description = Colors.UNDERLINE(
                f"Optional arguments for command {self._cli_action.action_name} to {Colors.BOLD(group_name)}",
            )
            argument_group = self._action_parser.add_argument_group(group_description)
            self._custom_arguments_groups[group_name] = argument_group
        return argument_group

    def _get_argument_group(self, argument) -> ArgumentGroup:
        if argument.argument_group_name is None:
            if argument.is_required():
                argument_group = self._required_arguments
            else:
                argument_group = self._optional_arguments
        else:
            argument_group = self._get_custom_argument_group(argument.argument_group_name)
        return argument_group

    def _setup_cli_app_options(self):
        executable = self._action_parser.prog.split()[0]
        tool_required_arguments = self._action_parser.add_argument_group(
            Colors.UNDERLINE(f"Required arguments for {Colors.BOLD(executable)}"),
        )
        tool_optional_arguments = self._action_parser.add_argument_group(
            Colors.UNDERLINE(f"Optional arguments for {Colors.BOLD(executable)}"),
        )
        for argument in self._cli_app.CLASS_ARGUMENTS:
            argument_group = tool_required_arguments if argument.is_required() else tool_optional_arguments
            argument.register(argument_group)

    def build(self) -> argparse.ArgumentParser:
        self.set_default_cli_options(self._action_parser)
        for argument in self._cli_action.arguments:
            argument_group = self._get_argument_group(argument)
            argument.register(argument_group)
        self._setup_cli_app_options()
        return self._action_parser
