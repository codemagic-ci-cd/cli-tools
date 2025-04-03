import argparse
import re
import shutil
import sys
from typing import Set

from .colors import Colors


class CliHelpFormatter(argparse.HelpFormatter):
    _suppressed_actions: Set[str] = set()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Fix help width
        if sys.stdout.isatty():
            self._width = shutil.get_terminal_size(fallback=(100, 24)).columns
        else:
            self._width = sys.maxsize

    @classmethod
    def suppress_action(cls, action_name: str):
        cls._suppressed_actions.add(action_name)

    def _exclude_suppressed_actions(self, message: str) -> str:
        for suppressed_action in self._suppressed_actions:
            message = re.sub(f"(?<=[^ ]){suppressed_action},?", "", message)
        return message

    def _format_args(self, *args, **kwargs):
        # Set custom color for arguments
        fmt = super()._format_args(*args, **kwargs)
        return Colors.CYAN(fmt)

    def _format_action_invocation(self, action):
        # Omit suppressed actions from help output and color
        # optional arguments as blue and mandatory as green
        fmt = super()._format_action_invocation(action)

        if action.dest == "action":
            fmt = self._exclude_suppressed_actions(fmt)

        parts = fmt.split(", ")
        color = Colors.BRIGHT_BLUE if action.option_strings else Colors.GREEN
        return ", ".join(map(color, parts))

    def _format_action(self, action):
        # Identical to superclass definition with exception in one if -branch:
        # `elif len(Colors.remove(action_header)) <= action_width`.
        # To cope with colored starts, the width of the actions is custom-calculated.

        # determine the required width and the entry label
        help_position = min(
            self._action_max_length + 2,
            self._max_help_position,
        )
        help_width = max(self._width - help_position, 11)
        action_width = help_position - self._current_indent - 2
        action_header = self._format_action_invocation(action)

        # no help; start on same line and add a final newline
        if not action.help:
            tup = self._current_indent, "", action_header
            action_header = "%*s%s\n" % tup

        # short action name; start on the same line and pad two spaces
        elif len(Colors.remove(action_header)) <= action_width:
            right_padding = max(0, action_width - len(Colors.remove(action_header))) + 2
            action_header = f"{' ' * self._current_indent}{action_header}{' ' * right_padding}"
            indent_first = 0

        # long action name; start on the next line
        else:
            tup = self._current_indent, "", action_header
            action_header = "%*s%s\n" % tup
            indent_first = help_position

        # collect the pieces of the action help
        parts = [action_header]

        # if there was help for the action, add lines of help text
        if action.help:
            help_text = self._expand_help(action)
            help_lines = self._split_lines(help_text, help_width)
            parts.append("%*s%s\n" % (indent_first, "", help_lines[0]))
            for line in help_lines[1:]:
                parts.append("%*s%s\n" % (help_position, "", line))

        # or add a newline if the description doesn't end with one
        elif not action_header.endswith("\n"):
            parts.append("\n")

        # if there are any sub-actions, add their help as well
        for subaction in self._iter_indented_subactions(action):
            parts.append(self._format_action(subaction))

        # return a single string
        return self._join_parts(parts)

    def _format_usage(self, *args, **kwargs) -> str:
        usage = super()._format_usage(*args, **kwargs)
        return self._exclude_suppressed_actions(usage)
