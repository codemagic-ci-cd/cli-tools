
from __future__ import annotations
import os
import sys
from typing import List, Tuple, NamedTuple
from mdutils.tools.tools import Table
from mdutils.mdutils import MdUtils
import mdutils
from pathlib import Path
import re
import argparse

sys.path.append(os.path.abspath('./src'))
from codemagic import cli
from codemagic import tools

SerializedArgument = NamedTuple('SerializedArgument', [
    ('key', str),
    ('description', str),
    ('flags', str),
    ('name', str),
    ('required', bool),
    ('default', str),
    ('nargs', bool),
    ('choices', str)
])

Action = NamedTuple('Action', [
    ('action_name', str),
    ('name', str),
    ('description', str),
    ('required_args', List[SerializedArgument]),
    ('optional_args', List[SerializedArgument])
])

ArgumentKwargs = NamedTuple('ArgumentKwargs', [
    ('nargs', bool),
    ('required', bool),
    ('default', str),
    ('choices', str)
])


class ArgumentsSerializer:
    def __init__(self, raw_arguments: Tuple):
        self.raw_arguments = raw_arguments
        self.required_args: List[SerializedArgument] = []
        self.optional_args: List[SerializedArgument] = []

    def serialize(self) -> ArgumentsSerializer:
        for arg in self.raw_arguments:
            arg_type = getattr(arg._value_, 'type')
            arg_type = arg_type.__name__ if arg_type else ''
            kwargs = self._proccess_kwargs(getattr(arg._value_, 'argparse_kwargs'))

            argument: SerializedArgument = SerializedArgument(
                key=arg._value_.key,
                description=str_plain(arg._value_.description),
                flags=', '.join(getattr(arg._value_, 'flags', '')),
                name='' if arg_type == 'bool' else arg._name_,
                required=kwargs.required,
                default=kwargs.default,
                nargs=kwargs.nargs,
                choices=kwargs.choices,
            )

            if argument.required:
                self.required_args.append(argument)
            else:
                self.optional_args.append(argument)
        return self

    def _proccess_kwargs(self, kwargs):
        def _process_choice(choices):
            return ' | '.join([str(c) for c in choices] if choices else '')

        def _process_default(default):
            if not default:
                return ''
            if isinstance(default, tuple) and isinstance(default[0], Path):
                default = default[0]
            if isinstance(default, Path):
                default = str(default).replace(str(Path.home()), '$HOME')
            return str(default)

        kwargs = kwargs if kwargs else {}
        return ArgumentKwargs(
            nargs=kwargs.get('nargs', '') == '+',
            required=kwargs.get('required', True),
            default=_process_default(kwargs.get('default', '')),
            choices=_process_choice(kwargs.get('choices'))
        )


# docs/README.md
class MainPageDocumentationGenerator:
    def __init__(self, title: str, main_dir: str):
        self.title = title
        self.main_dir = main_dir

    def generate(self, tools: List):
        os.makedirs(self.main_dir, exist_ok=True)
        md = MdUtils(file_name=f'{self.main_dir}/README', title=self.title)
        Writer(md).write_tools_table(tools)
        md.create_md_file()


class ToolDocumentationGenerator:
    def __init__(self, tool, main_dir: str):
        self.tool = tool
        self.tool_name: str = tool.__name__
        self.tool_command: str = get_tool_command(self.tool_name)
        self.tool_prefix: str = f'{main_dir}/{self.tool_command}'

    def generate(self):
        class_args_serializer = ArgumentsSerializer(self.tool.CLASS_ARGUMENTS).serialize()
        self.tool_optional_args = class_args_serializer.optional_args
        self.tool_serialized_actions = self._serialize_actions()
        self.tool_options = self._serialize_default_options()

        # docs/<tool-name>.md
        md = MdUtils(file_name=f'{self.tool_prefix}', title=self.tool_name)
        writer = Writer(md)
        writer.write_tool_command_usage(self)
        writer.write_description(self.tool.__doc__)
        writer.write_options(self.tool_options)
        writer.write_arguments(self.tool_command, self.tool_optional_args, [])
        writer.write_actions_table(self.tool_command, self.tool_serialized_actions)
        md.create_md_file()

        for action in self.tool_serialized_actions:
            # docs/<tool-name>_<action-name>.md
            md = MdUtils(file_name=f'{self.tool_prefix}_{action.action_name}', title=action.name)
            writer = Writer(md)
            writer.write_action_command_usage(self, action)
            writer.write_description(action.description)
            writer.write_options(self.tool_options)
            writer.write_arguments(f'command {action.name}', action.optional_args, action.required_args)
            writer.write_arguments(self.tool_command, self.tool_optional_args, [])
            md.create_md_file()

    def _serialize_actions(self):
        serialized_actions: List[Action] = []
        for f in self.tool.get_class_cli_actions():
            action_args_serializer = ArgumentsSerializer(f.arguments).serialize()
            serialized_actions.append(Action(
                action_name=f.action_name,
                name=f.__name__,
                description=f.__doc__,
                required_args=action_args_serializer.required_args,
                optional_args=action_args_serializer.optional_args,

            ))
        return serialized_actions

    def _serialize_default_options(self):
        def _serialize_option(option):
            return SerializedArgument(
                key='',
                description=str_plain(str(option.help)).replace('[','').replace(']',''),
                flags=', '.join(option.option_strings),
                name='',
                required=False,
                default='',
                nargs=False,
                choices='|'.join(option.choices) if option.choices else '',
            )

        parser = argparse.ArgumentParser(
            description=self.tool.__doc__,
            formatter_class=cli.cli_help_formatter.CliHelpFormatter
        )
        self.tool.get_default_cli_options(parser)
        return [_serialize_option(arg) for arg in parser._actions]


class CommandUsageGenerator:
    def __init__(self, doc_generator: ToolDocumentationGenerator):
        self.doc_generator = doc_generator

    def get_tool_command_usage(self) -> str:
        return f'{self.doc_generator.tool_command} {self._get_tool_flags()} ACTION'

    def get_action_command_usage(self, action: Action) -> str:
        tool_flags = self._get_tool_flags()
        optional_flags = self._prepare_arguments(action.optional_args)
        required_flags = self._prepare_arguments(action.required_args)
        return f'{self.doc_generator.tool_command} {action.action_name} {tool_flags} {optional_flags} {required_flags}'

    def _get_tool_flags(self):
        optional_common_flags = self._prepare_arguments(self.doc_generator.tool_options)
        tool_flags = self._prepare_arguments(self.doc_generator.tool_optional_args)
        return f'{optional_common_flags} {tool_flags}'

    def _get_formatted_flag(self, arg):
        flag = f'{arg.flags.split(",")[0]}'
        if not arg.flags and arg.name:
            flag = arg.name
        elif arg.choices and not arg.name:
            flag = f'{flag} CHOSEN_OPTION'
        elif arg.name:
            flag = f'{flag} {arg.name}'
        return flag if arg.required else f'[{flag}]'

    def _prepare_arguments(self, args):
        return ' '.join([self._get_formatted_flag(arg) for arg in args])


class Writer:
    def __init__(self, file: MdUtils):
        self.file = file

    def write_description(self, content: str):
        content = str_plain(content)
        self.file.new_header(level=4, title=content)

    def write_tool_command_usage(self, documentation_generator: ToolDocumentationGenerator):
        content = CommandUsageGenerator(documentation_generator).get_tool_command_usage()
        self.file.new_paragraph(f"``{content}``")

    def write_action_command_usage(self, documentation_generator: ToolDocumentationGenerator, action: Action):
        content = CommandUsageGenerator(documentation_generator).get_action_command_usage(action)
        self.file.new_paragraph(f"``{content}``")

    def write_table(self, content: List[List[str]], header: List[str]):
        flat_content: List[str] = sum(content, [])
        table = Table().create_table(
            columns=len(header),
            rows=len(content) + 1,
            text=header + flat_content,
            text_align='left'
        )
        self.file.write(table)

    def write_tools_table(self, tools: List):
        def _get_tool_link(name):
            command = get_tool_command(name)
            return f'[{name}]({command}.md)'

        content = [
            [
                _get_tool_link(tool.__name__),
                str_plain(tool.__doc__)
            ] for tool in tools]
        self.write_table(content, ['Tool name', 'Description'])

    def write_actions_table(self, tool_command: str, actions: List[Action]):
        self.file.new_header(level=3, title='Actions')
        content = [
            [
                f'[{action.action_name}]({tool_command}_{action.action_name}.md)',
                str_plain(action.description)
            ] for action in actions]
        self.write_table(content, ['Action', 'Description'])

    def write_arguments(self, obj: str, optional: List[SerializedArgument], required: List[SerializedArgument]):
        self._write_arguments(f'Required arguments for {obj}', required)
        self._write_arguments(f'Optional arguments for {obj}', optional)

    def write_options(self, options: List[SerializedArgument]):
        self._write_arguments(f'Optional arguments', options)

    def _write_arguments(self, title, args):
        def _process_flag(arg):
            flag: str = arg.flags
            if flag and arg.choices:
                return f'{flag}={arg.choices}'
            if flag and arg.name:
                return f'{flag}={arg.name}'
            return arg.name if arg.name else flag

        def _process_description(arg):
            description: str = arg.description
            description += '. Multiple arguments' if arg.nargs else ''
            return f'{description}. Default:&nbsp;`{arg.default}`' if arg.default else description

        if not args:
            return

        self.file.new_header(level=3, title=title)
        for arg in args:
            flag = _process_flag(arg)
            description = _process_description(arg).replace('..', '.')
            self.file.new_paragraph(f'**{flag}**')
            self.file.new_paragraph(description)


def get_tool_command(tool_name):
    tool_commands = {
        'AppStoreConnect': 'app-store-connect',
        'GitChangelog': 'git-changelog',
        'Keychain': 'keychain',
        'UniversalApkGenerator': 'universal-apk',
        'XcodeProject': 'xcode-project'
    }
    return tool_commands[tool_name]


def str_plain(string):
    return re.compile('(\\x1b\[\d*m|\\x1b\[\d*m|\\n|\\t)').sub('', string).strip()


def main():
    main_dir = 'docs'
    tools = cli.CliApp.__subclasses__()
    MainPageDocumentationGenerator('CLI tools', main_dir).generate(tools)
    for tool in tools:
        ToolDocumentationGenerator(tool, main_dir).generate()


if __name__ == "__main__":
    main()
