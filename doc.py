import os
import sys
from types import FunctionType
from mdutils.tools.tools import Table
from mdutils.mdutils import MdUtils
import mdutils
from pathlib import Path
import re

sys.path.append(os.path.abspath('./src'))
from codemagic import cli
from codemagic import tools

class ArgumentsSerializer:
    def __init__(self, raw_arguments):
        self.raw_arguments = raw_arguments
        self.required_args = []
        self.optional_args = []

    def serialize(self):
        for arg in self.raw_arguments:
            argument = {
                'key': arg._value_.key,
                'description': str_plain(arg._value_.description),
                'flags': ', '.join(getattr(arg._value_, 'flags', '')),
            }
            argument.update(self._proccess_kwargs(
                getattr(arg._value_, 'argparse_kwargs')))

            arg_type = getattr(arg._value_, 'type')
            argument['type'] = arg_type.__name__ if arg_type else ''
            argument['name'] = '' if argument['type'] == 'bool' else arg._name_

            if argument['required']:
                self.required_args.append(argument)
            else:
                self.optional_args.append(argument)
        return self

    def _proccess_kwargs(self, kwargs):
        def _process_choice(choices):
            choices = [str(c) for c in choices] if choices else ''
            return '<br />'.join(choices)

        def _process_default(default):
            if isinstance(default, tuple) and isinstance(default[0], Path):
                default = default[0]
            if isinstance(default, Path):
                default = str(default).replace(str(Path.home()), '$HOME')
            return str(default).replace('|', '&#124;') if default else ''

        kwargs = kwargs if kwargs else {}
        return {
            'nargs': 'Yes' if kwargs.get('nargs', '') == '+' else '',
            'required': kwargs.get('required', True),
            'default': _process_default(kwargs.get('default', '')),
            'choices': _process_choice(kwargs.get('choices')),
        }


# docs/README.md
class MainPageDocumentationGenerator:
    def __init__(self, title, main_dir):
        self.title = title
        self.main_dir = main_dir

    def generate(self, tools):
        os.makedirs(self.main_dir, exist_ok=True)
        md = MdUtils(file_name=f'{self.main_dir}/README', title=self.title)
        Writer(md).write_tools_table(tools)
        md.create_md_file()


class ToolDocumentationGenerator:
    def __init__(self, tool, main_dir):
        self.tool = tool
        self.tool_name = tool.__name__
        self.tool_dir_name = f'{main_dir}/{self.tool_name}'

    def generate(self):
        os.makedirs(self.tool_dir_name, exist_ok=True)

        class_args_serializer = ArgumentsSerializer(self.tool.CLASS_ARGUMENTS).serialize()
        self.tool_required_args = class_args_serializer.required_args
        self.tool_optional_args = class_args_serializer.optional_args
        self.tool_serialized_actions = self._serialize_actions()
        self.tool_optinal_argument, self.tool_options = self._serialize_default_options()

        # docs/<tool-name>/README.md
        md = MdUtils(file_name=f'{self.tool_dir_name}/README', title=self.tool_name)
        writer = Writer(md)
        writer.write_tool_command_usage(self)
        writer.write_description(self.tool.__doc__)
        writer.write_options_tables(self.tool_optinal_argument, self.tool_options)
        writer.write_actions_table(self.tool_name, self.tool_serialized_actions)
        writer.write_arguments_tables(self.tool_name, self.tool_required_args, self.tool_optional_args)
        md.create_md_file()

        for action in self.tool_serialized_actions:
            # docs/<tool-name>/<action-name>/README.md
            dir_name = f'{self.tool_dir_name}/{action["name"]}'
            os.makedirs(f'{dir_name}', exist_ok=True)

            md = MdUtils(file_name=f'{dir_name}/README', title=action['name'])
            writer = Writer(md)
            writer.write_action_command_usage(self, action)
            writer.write_description(action['description'])
            writer.write_options_tables(self.tool_optinal_argument, self.tool_options)
            writer.write_arguments_tables(f'command {action["name"]}', action['required_args'], action['optional_args'])
            writer.write_arguments_tables(self.tool_name, self.tool_required_args, self.tool_optional_args)
            md.create_md_file()

    def _serialize_actions(self):
        serialized_actions = []
        for f in self.tool.get_class_cli_actions():
            action_args_serializer = ArgumentsSerializer(f.arguments).serialize()
            serialized_actions.append({
                'action_name': f.action_name,
                'name': f.__name__,
                'description': f.__doc__,
                'required_args': action_args_serializer.required_args,
                'optional_args': action_args_serializer.optional_args,
            })
        return serialized_actions

    def _serialize_default_options(self):
        import argparse
        from codemagic.cli.cli_help_formatter import CliHelpFormatter

        def _serialize_option(option):
            return {
                'flags': ', '.join(option.option_strings),
                'description': str_plain(option.help),
                'choices': ', '.join(option.choices) if option.choices else '',
            }

        parser = argparse.ArgumentParser(description=self.tool.__doc__, formatter_class=CliHelpFormatter)
        self.tool.get_default_cli_options(parser)
        possible_arguments = parser._actions
        help_option = {}
        options = []
        for arg in possible_arguments:
            if arg.dest == 'help':
                help_option = _serialize_option(arg)
            else:
                options.append(_serialize_option(arg))
        return help_option, options


class CommandUsageGenerator:
    def __init__(self, doc_generator):
        self.doc_generator = doc_generator
        self.tool_name = self._get_tool_name()

    def get_tool_command_usage(self):
        tool_actions = self._wrap_in_brackets(', '.join(
            [action['name'] for action in self.doc_generator.tool_serialized_actions]
        ))
        return f'{self.tool_name} {self._get_optional_common_flags()} {tool_actions}'

    def get_action_command_usage(self, action):
        from pprint import pprint
        optional_common_flags = self._get_optional_common_flags()
        optional_flags = self._prepare_action_arguments(action['optional_args'])
        required_flags = self._prepare_action_arguments(action['required_args'])
        return f'{self.tool_name} {action["action_name"]} {optional_common_flags} {optional_flags} {required_flags}'

    def _get_tool_name(self):
        tool_names = {
            'AppStoreConnect': 'app-store-connect',
            'GitChangelog': 'git-changelog',
            'Keychain': 'keychain',
            'UniversalApkGenerator': 'universal-apk',
            'XcodeProject': 'xcode-project'
        }
        return tool_names[self.doc_generator.tool.__name__]

    def _get_formatted_flag(self, arg):
        if not arg['flags'] and 'name' in arg:
            return arg['name']
        flag = f'{arg["flags"].split(",")[0]}'
        if arg['choices']:
            return f'[{flag} {self._wrap_in_brackets(arg["choices"])}]'
        if 'name' in arg and arg['name']:
            return f'[{flag} {arg["name"]}]'
        return f'[{flag}]'

    def _wrap_in_brackets(self, string):
        l_br, r_br = '{', '}'
        return f'{l_br}{string}{r_br}'

    def _get_optional_common_flags(self):
        help_option = self._get_formatted_flag(self.doc_generator.tool_optinal_argument)
        tool_options = ' '.join(
            [self._get_formatted_flag(option) for option in self.doc_generator.tool_options]
        )
        return f'{help_option} {tool_options}'

    def _prepare_action_arguments(self, args):
        def _remove_styling_from_arg(arg):
            arg['choices'] = arg['choices'].replace('<br />', ', ')
            return arg

        args_without_styling = [_remove_styling_from_arg(arg) for arg in args]
        return ' '.join([self._get_formatted_flag(arg) for arg in args_without_styling])


class Writer:
    def __init__(self, file):
        self.file = file

    def write_description(self, content):
        content = str_plain(content)
        self.file.new_header(level=4, title=content)

    def write_tool_command_usage(self, documentation_generator):
        content = CommandUsageGenerator(documentation_generator).get_tool_command_usage()
        self.file.new_paragraph(f"``{content}``")

    def write_action_command_usage(self, documentation_generator, action):
        content = CommandUsageGenerator(documentation_generator).get_action_command_usage(action)
        self.file.new_paragraph(f"``{content}``")

    def write_table(self, content, header):
        flat_content = sum(content, [])
        table = Table().create_table(
            columns=len(header),
            rows=len(content) + 1,
            text=header + flat_content,
            text_align='left'
        )
        self.file.write(table)

    def write_tools_table(self, tools):
        tools_source = [
            [
                f'[{tool.__name__}]({tool.__name__}/README.md)',
                str_plain(tool.__doc__)
            ] for tool in tools]
        self.write_table(tools_source, ['Tool name', 'Description'])

    def write_actions_table(self, tool_name, actions):
        self.file.new_header(level=3, title=f'{tool_name} actions')
        actions_source = [
            [
                f'[{action["name"]}]({action["name"]}/README.md)',
                str_plain(action['description'])
            ] for action in actions]
        self.write_table(actions_source, ['Action', 'Description'])

    def write_arguments_tables(self, obj, required, optional):
        self._write_arguments_table(f'Required arguments for {obj}', required)
        self._write_arguments_table(f'Optional arguments for {obj}', optional)

    def write_options_tables(self, help_option, options):
        self._write_arguments_table(f'Optional arguments', [help_option])
        self._write_arguments_table(f'Options', options)

    def _write_arguments_table(self, title, args):
        if not args:
            return

        parameters_to_show = []

        if [arg['flags'] for arg in args if arg.get('flags')]:
            parameters_to_show.append({'name': 'flags', 'header': 'Flags'})
        if [arg['name'] for arg in args if arg.get('name')]:
            parameters_to_show.append({'name': 'name', 'header': 'Argument'})
        if [arg['description'] for arg in args if arg.get('description')]:
            parameters_to_show.append({'name': 'description', 'header': 'Description'})
        if [arg['type'] for arg in args if arg.get('type')]:
            parameters_to_show.append({'name': 'type', 'header': 'Type'})
        if [arg['default'] for arg in args if arg.get('default')]:
            parameters_to_show.append({'name': 'default', 'header': 'Default'})
        if [arg['nargs'] for arg in args if arg.get('nargs')]:
            parameters_to_show.append({'name': 'nargs', 'header': 'Multiple arguments'})
        if [arg['choices'] for arg in args if arg.get('choices')]:
            parameters_to_show.append({'name': 'choices', 'header': 'Choices'})

        header = [parameter['header'] for parameter in parameters_to_show]
        content = [
            [
                arg[parameter['name']] for parameter in parameters_to_show
            ] for arg in args]

        self.file.new_header(level=3, title=title)
        self.write_table(content, header)


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
