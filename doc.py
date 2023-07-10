#!/usr/bin/env python3

from __future__ import annotations

import argparse
import operator
import os
import re
import sys
from collections import defaultdict
from functools import reduce
from pathlib import Path
from typing import Dict
from typing import Iterable
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Sequence

from mdutils.mdutils import MdUtils
from mdutils.tools.Table import Table

sys.path.insert(0, os.path.abspath("./src"))

from codemagic import cli
from codemagic import tools


class SerializedArgument(NamedTuple):
    key: str
    description: str
    flags: str
    name: str
    required: bool
    argument_group_name: Optional[str]
    default: str
    nargs: bool
    choices: str
    store_boolean: bool


class Action(NamedTuple):
    action_name: str
    name: str
    description: str
    required_args: List[SerializedArgument]
    optional_args: List[SerializedArgument]
    custom_args: Dict[str, List[SerializedArgument]]


class ActionGroup(NamedTuple):
    name: str
    description: str
    actions: List[Action]


class ArgumentKwargs(NamedTuple):
    nargs: bool
    required: bool
    default: str
    choices: str
    store_boolean: bool


class ArgumentsSerializer:
    def __init__(self, raw_arguments: Sequence[cli.Argument]):
        self.raw_arguments = raw_arguments
        self.required_args: List[SerializedArgument] = []
        self.optional_args: List[SerializedArgument] = []
        self.custom_args: Dict[str, List[SerializedArgument]] = defaultdict(list)

    @classmethod
    def _replace_quotes(cls, description: str) -> str:
        json_array = re.compile(r'"(\[[^\]]+\])"')
        json_object = re.compile(r'"(\{[^\}]+\})"')
        # Dummy handling for description containing JSON arrays and objects as an example
        for patt in (json_object, json_array):
            if not patt.search(description):
                continue
            before, obj, after = patt.split(description)
            before = before.replace('"', "`")
            after = after.replace('"', "`")
            return f"{before}`{obj}`{after}"
        return description.replace('"', "`")

    def _serialize_argument(self, arg) -> SerializedArgument:
        description = str_plain(arg._value_.description)
        arg_type = getattr(arg._value_, "type")
        if isinstance(arg_type, type) and issubclass(arg_type, cli.argument.TypedCliArgument):
            description = str_plain(arg.get_description())
            env_var = arg_type.__dict__.get("environment_variable_key")
            to_match = f"{env_var}|{arg._name_}" if env_var else arg._name_
            description = re.sub(f"(\\s?)({to_match})(\\s?)", r"\1`\2`\3", description)
            description = self._replace_quotes(description)

        kwargs = self._proccess_kwargs(getattr(arg._value_, "argparse_kwargs"))
        return SerializedArgument(
            key=arg._value_.key,
            description=description,
            flags=", ".join(getattr(arg._value_, "flags", "")),
            name="" if arg_type and arg_type.__name__ == "bool" else arg._name_,
            required=kwargs.required,
            argument_group_name=arg._value_.argument_group_name,
            default=kwargs.default,
            nargs=kwargs.nargs,
            choices=kwargs.choices,
            store_boolean=kwargs.store_boolean,
        )

    def serialize(self) -> ArgumentsSerializer:
        for argument in map(self._serialize_argument, self.raw_arguments):
            if argument.required:
                self.required_args.append(argument)
            elif argument.argument_group_name:
                self.custom_args[argument.argument_group_name].append(argument)
            else:
                self.optional_args.append(argument)
        return self

    @classmethod
    def _proccess_kwargs(cls, kwargs):
        def _process_choice(choices):
            return " | ".join([str(c) for c in choices] if choices else "")

        def _process_default(default):
            if not default:
                return ""
            if isinstance(default, tuple) and len(default) > 1 and isinstance(default[0], Path):
                default = ", ".join(str(p).replace(str(Path.home()), "$HOME") for p in default)
            if isinstance(default, tuple) and isinstance(default[0], Path):
                default = default[0]
            if isinstance(default, Path):
                default = str(default).replace(str(Path.home()), "$HOME")
            return str(default)

        kwargs = kwargs or {}
        return ArgumentKwargs(
            nargs=kwargs.get("nargs", "") == "+",
            required=kwargs.get("required", True),
            default=_process_default(kwargs.get("default", "")),
            choices=_process_choice(kwargs.get("choices")),
            store_boolean=kwargs.get("action") in ("store_true", "store_false"),
        )


# docs/README.md
class MainPageDocumentationGenerator:
    def __init__(self, title: str, main_dir: str):
        self.title = title
        self.main_dir = main_dir

    def generate(self, tools: List[cli.CliApp]):
        os.makedirs(self.main_dir, exist_ok=True)
        md = MdUtils(file_name=f"{self.main_dir}/README", title=self.title)
        Writer(md).write_tools_table(tools)
        md.create_md_file()


class ToolDocumentationGenerator:
    def __init__(self, tool, main_dir: str):
        class_args_serializer = ArgumentsSerializer(tool.CLASS_ARGUMENTS).serialize()

        self.tool = tool
        self.tool_command = tool.get_executable_name()
        self.tool_prefix = f"{main_dir}/{self.tool_command}"
        self.tool_optional_args = class_args_serializer.optional_args
        self.tool_required_args = class_args_serializer.required_args
        self.tool_options = self._serialize_default_options(self.tool)
        self.tool_serialized_actions = self._serialize_actions(self.tool)
        self.tool_serialized_action_groups = self._serialize_action_groups(self.tool)

    def generate(self):
        self._write_tool_page()

        for action in self.tool_serialized_actions:
            self._write_action_page(action)

        for group in self.tool_serialized_action_groups:
            self._write_action_group_page(group)

    def _write_tool_command_arguments_and_options(self, writer):
        writer.write_arguments(f"command `{self.tool_command}`", self.tool_optional_args, self.tool_required_args, {})
        writer.write_options(self.tool_options)

    def _write_tool_page(self):
        os.makedirs(self.tool_prefix, exist_ok=True)
        md = MdUtils(file_name=f"{self.tool_prefix}/README", title=self.tool_command)
        writer = Writer(md)
        writer.write_description(self.tool.__doc__)
        writer.write_command_usage(self)
        self._write_tool_command_arguments_and_options(writer)
        writer.write_actions_table(self.tool_serialized_actions)
        writer.write_action_groups_table(self.tool_serialized_action_groups)
        md.create_md_file()

    def _write_action_group_page(self, action_group: ActionGroup):
        group_path = f"{self.tool_prefix}/{action_group.name}"
        md = MdUtils(file_name=group_path, title=action_group.name)
        writer = Writer(md)
        writer.write_description(action_group.description)
        writer.write_command_usage(self, action_group=action_group)
        self._write_tool_command_arguments_and_options(writer)
        writer.write_actions_table(action_group.actions, action_group=action_group)
        md.create_md_file()
        os.makedirs(group_path, exist_ok=True)
        for action in action_group.actions:
            self._write_action_page(action, action_group=action_group)

    def _write_action_page(self, action: Action, action_group: Optional[ActionGroup] = None):
        group_str = f"{action_group.name}/" if action_group else ""
        md = MdUtils(file_name=f"{self.tool_prefix}/{group_str}{action.action_name}", title=action.action_name)
        writer = Writer(md)
        writer.write_description(action.description)
        writer.write_command_usage(self, action_group=action_group, action=action)
        writer.write_arguments(
            f"action `{action.action_name}`",
            action.optional_args,
            action.required_args,
            action.custom_args,
        )
        self._write_tool_command_arguments_and_options(writer)
        md.create_md_file()

    @classmethod
    def _serialize_action_groups(cls, tool: cli.CliApp) -> List[ActionGroup]:
        def _serialize_action_group(group) -> ActionGroup:
            return ActionGroup(
                name=group.name,
                description=group.description,
                actions=cls._serialize_actions(tool, action_group=group),
            )

        return list(map(_serialize_action_group, tool.list_class_action_groups()))

    @classmethod
    def _serialize_actions(cls, tool: cli.CliApp, action_group=None) -> List[Action]:
        def _serialize_action(action: cli.argument.ActionCallable) -> Action:
            assert isinstance(action.__doc__, str)
            action_args_serializer = ArgumentsSerializer(action.arguments).serialize()
            return Action(
                action_name=action.action_name,
                name=action.__name__,
                description=action.__doc__,
                required_args=action_args_serializer.required_args,
                optional_args=action_args_serializer.optional_args,
                custom_args=action_args_serializer.custom_args,
            )

        return list(map(_serialize_action, tool.iter_class_cli_actions(action_group=action_group)))

    @classmethod
    def _serialize_default_options(cls, tool: cli.CliApp) -> List[SerializedArgument]:
        def _serialize_option(option) -> SerializedArgument:
            return SerializedArgument(
                key="",
                description=str_plain(str(option.help)).replace("[", "").replace(": ", " `").replace("]", "`"),
                flags=", ".join(option.option_strings),
                name="",
                required=False,
                argument_group_name=None,
                default="",
                nargs=False,
                choices=" | ".join(option.choices) if option.choices else "",
                store_boolean=str(type(option)) in ("_StoreTrueAction", "_StoreFalseAction"),
            )

        parser = argparse.ArgumentParser(
            description=tool.__doc__,
            formatter_class=cli.cli_help_formatter.CliHelpFormatter,
        )
        cli.argument.ArgumentParserBuilder.set_default_cli_options(parser)
        return list(map(_serialize_option, parser._actions))


class CommandUsageGenerator:
    def __init__(self, doc_generator: ToolDocumentationGenerator):
        self.doc_generator = doc_generator

    def get_command_usage(
        self,
        action_group: Optional[ActionGroup] = None,
        action: Optional[Action] = None,
    ) -> List[str]:
        action_group_str = f" {action_group.name}" if action_group else ""
        action_str = f" {action.action_name}" if action else ""

        action_args = (
            [
                *map(self._get_formatted_flag, action.optional_args),
                *map(self._get_formatted_flag, action.required_args),
                *map(self._get_formatted_flag, reduce(operator.add, action.custom_args.values(), [])),
            ]
            if action
            else ["ACTION"]
        )

        return [
            f"{self.doc_generator.tool_command}{action_group_str}{action_str} {self._get_opt_common_flags()}",
            *self._get_tool_arguments_and_flags(),
            *action_args,
        ]

    def _get_opt_common_flags(self) -> str:
        return " ".join(map(self._get_formatted_flag, self.doc_generator.tool_options))

    def _get_tool_arguments_and_flags(self) -> Iterable[str]:
        return map(
            self._get_formatted_flag,
            [*self.doc_generator.tool_required_args, *self.doc_generator.tool_optional_args],
        )

    @classmethod
    def _get_formatted_flag(cls, arg: SerializedArgument) -> str:
        flag = f'{arg.flags.split(",")[0]}'
        if arg.store_boolean:
            pass
        elif not arg.flags and arg.name:
            flag = arg.name
        elif arg.choices and not arg.name:
            flag = f"{flag} STREAM"
        elif arg.name:
            flag = f"{flag} {arg.name}"
        return flag if arg.required else f"[{flag}]"


class Writer:
    def __init__(self, file: MdUtils):
        self.file = file

    def write_description(self, content: str):
        content = str_plain(content)
        self.file.new_paragraph(f"**{content}**", wrap_width=0)

    def write_command_usage(
        self,
        generator: ToolDocumentationGenerator,
        action_group: Optional[ActionGroup] = None,
        action: Optional[Action] = None,
    ):
        lines = CommandUsageGenerator(generator).get_command_usage(action_group=action_group, action=action)
        self._write_command_usage(self.file, lines)

    def write_table(self, content: List[List[str]], header: List[str]):
        flat_content: List[str] = sum(content, [])
        table = Table().create_table(
            columns=len(header),
            rows=len(content) + 1,
            text=header + flat_content,
            text_align="left",
        )
        self.file.write(table, wrap_width=0)

    def write_tools_table(self, tools: List[cli.CliApp]):
        def _get_tool_link(tool: cli.CliApp) -> str:
            return f"[`{tool.get_executable_name()}`]({tool.get_executable_name()}/README.md)"

        def _get_tool_doc(tool: cli.CliApp) -> List[str]:
            assert isinstance(tool.__doc__, str)
            return [_get_tool_link(tool), str_plain(tool.__doc__)]

        self.write_table(list(map(_get_tool_doc, tools)), ["Tool name", "Description"])

    def write_actions_table(self, actions: List[Action], action_group: Optional[ActionGroup] = None):
        if not actions:
            return

        def _get_action_doc(action: Action) -> List[str]:
            action_group_str = f"{action_group.name}/" if action_group else ""
            action_link = f"{action_group_str}{action.action_name}.md"
            return [f"[`{action.action_name}`]({action_link})", str_plain(action.description)]

        self.file.new_header(level=3, title="Actions", add_table_of_contents="n")
        self.write_table(list(map(_get_action_doc, actions)), ["Action", "Description"])

    def write_action_groups_table(self, groups: List[ActionGroup]):
        if not groups:
            return

        def _get_group_doc(group: ActionGroup) -> List[str]:
            return [f"[`{group.name}`]({group.name}.md)", str_plain(group.description)]

        self.file.new_header(level=3, title="Action groups", add_table_of_contents="n")
        self.write_table(list(map(_get_group_doc, groups)), ["Action group", "Description"])

    def write_arguments(
        self,
        obj: str,
        optional: List[SerializedArgument],
        required: List[SerializedArgument],
        custom: Dict[str, List[SerializedArgument]],
    ):
        self._write_arguments(self.file, f"Required arguments for {obj}", required)
        self._write_arguments(self.file, f"Optional arguments for {obj}", optional)
        for group_name, custom_arguments in custom.items():
            self._write_arguments(self.file, f"Optional arguments to {group_name}", custom_arguments)

    def write_options(self, options: List[SerializedArgument]):
        self._write_arguments(self.file, "Common options", options)

    @classmethod
    def _write_command_usage(cls, file: MdUtils, lines: List[str]):
        file.new_header(level=3, title="Usage", add_table_of_contents="n")
        main_lines = "".join([f"    {line}\n" for line in lines[1:]])
        file.write(f"```bash\n{lines[0]}\n{main_lines}```", wrap_width=0)

    @classmethod
    def _write_arguments(cls, file: MdUtils, title: str, args: List[SerializedArgument]):
        def _process_flag(arg: SerializedArgument) -> str:
            flag = arg.flags
            if arg.store_boolean:
                return flag
            if flag and arg.choices:
                return f"{flag}={arg.choices}"
            if flag and arg.name:
                return f"{flag}={arg.name}"
            return arg.name if arg.name else flag

        def _process_description(argument: SerializedArgument) -> str:
            _description = argument.description.replace("*", r"\*").replace(r"\*\*", "**")
            _description += ". Multiple arguments" if argument.nargs else ""
            if argument.default and "[Default:" not in _description:
                return f"{_description}. Default:&nbsp;`{argument.default}`"
            else:
                return _description

        if not args:
            return

        file.new_header(level=3, title=title, add_table_of_contents="n")
        for arg in args:
            description = _process_description(arg).replace("..", ".")
            file.new_header(level=5, title=f"`{_process_flag(arg)}`", add_table_of_contents="n")
            file.new_paragraph(description, wrap_width=0)


def str_plain(string: str) -> str:
    bold = re.escape(cli.Colors.BOLD.value)
    blue = re.escape(cli.Colors.BRIGHT_BLUE.value)
    reset = re.escape(cli.Colors.RESET.value)

    string = re.sub(f"{bold}([^\x1b]+){reset}", r"**\1**", string)  # Convert ANSI bold to markdown bold
    string = re.sub(f"([^`]){blue}([^\x1b]+){reset}([^`])", r"\1`\2`\3", string)  # Convert ANSI blue to backticks
    string = re.sub(r"\x1b\[\d*m", "", string)  # Remove all other ANSI formatting
    return re.sub(r"\n|\t", " ", string).strip()  # Remove newlines and tabs


def main():
    print(f"Generate documentation for module {tools.__name__} from {tools.__file__}")
    main_dir = "docs"
    tool_classes = cli.CliApp.__subclasses__()
    MainPageDocumentationGenerator("CLI tools", main_dir).generate(tool_classes)
    for tool_class in tool_classes:
        print(f"Generate documentation for tool {tool_class.get_executable_name()}")
        ToolDocumentationGenerator(tool_class, main_dir).generate()


if __name__ == "__main__":
    main()
