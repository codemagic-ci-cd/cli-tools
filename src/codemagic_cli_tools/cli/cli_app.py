#!/usr/bin/env python3

from __future__ import annotations

import abc
import argparse
import logging
import os
import pathlib
import re
import shlex
import shutil
import sys
from functools import wraps
from itertools import chain
from typing import NoReturn, Optional, Sequence, Iterable, Type, List, Tuple

from .argument import Argument, ActionCallable
from .cli_process import CliProcess
from .cli_types import CommandArg, ObfuscatedCommand, ObfuscationPattern
from .color import Color


class CliAppException(Exception):

    def __init__(self, message: str, cli_process: Optional[CliProcess] = None):
        self.cli_process = cli_process
        self.message = message

    def __str__(self):
        if not self.cli_process:
            return self.message
        return f'Running {self.cli_process.safe_form} failed with exit code {self.cli_process.returncode}: {self.message}'


class CliApp(metaclass=abc.ABCMeta):
    _CLASS_ARGUMENTS: Tuple[Argument, ...] = tuple()
    CLI_EXCEPTION_TYPE: Type[CliAppException] = CliAppException

    def __init__(self, dry=False):
        self.dry_run = dry
        self.default_obfuscation = []
        self.obfuscation = 8 * '*'
        self.logger = logging.getLogger(self.__class__.__name__)

    @classmethod
    def from_cli_args(cls, cli_args: argparse.Namespace):
        return cls(**{argument.value.key: argument.from_args(cli_args) for argument in cls._CLASS_ARGUMENTS})

    @classmethod
    def _handle_cli_exception(cls, cli_exception: CliAppException) -> int:
        sys.stderr.write(f'{Color.RED(cli_exception.message)}\n')
        if cli_exception.cli_process:
            return cli_exception.cli_process.returncode
        else:
            return 1

    @classmethod
    def invoke_cli(cls):
        parser = cls._setup_cli_options()
        args = parser.parse_args()
        cls._setup_logging(args)

        try:
            instance = cls.from_cli_args(args)
        except argparse.ArgumentError as argument_error:
            parser.error(argument_error)

        cli_action = {ac.action_name: ac for ac in instance.get_cli_actions()}[args.action]
        action_args = {
            arg_type.value.key: arg_type.value.from_args(args, arg_type.get_default())
            for arg_type in cli_action.arguments
        }
        try:
            cli_action(**action_args)
            return 0
        except cls.CLI_EXCEPTION_TYPE as cli_exception:
            return cls._handle_cli_exception(cli_exception)

    @classmethod
    def get_class_cli_actions(cls) -> Iterable[ActionCallable]:
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if callable(attr) and getattr(attr, 'is_cli_action', False):
                yield attr

    def get_cli_actions(self) -> Iterable[ActionCallable]:
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and getattr(attr, 'is_cli_action', False):
                yield attr

    @classmethod
    def _setup_logging(cls, cli_args: argparse.Namespace):
        if not cli_args.log_commands:
            return

        stream = {'stderr': sys.stderr, 'stdout': sys.stdout}[cli_args.log_stream]
        log_level = logging.DEBUG if cli_args.verbose else logging.INFO
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s > %(message)s', '%m-%d %H:%M:%S')

        handler = logging.StreamHandler(stream)
        handler.setLevel(log_level)
        handler.setFormatter(formatter)

        logger = logging.getLogger()
        logger.addHandler(handler)
        logger.setLevel(log_level)

    @classmethod
    def _setup_default_cli_options(cls, action_parser):
        action_parser.add_argument('--disable-logging', dest='log_commands', action='store_false',
                                   help='Disable log output for actions')
        action_parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                                   help='Enable verbose logging')
        action_parser.add_argument('--log-stream', type=str, default='stderr', choices=['stderr', 'stdout'],
                                   help='Choose which stream to use for log output. [Default: stderr]')
        action_parser.set_defaults(verbose=False, log_commands=True)

    @classmethod
    def _setup_cli_options(cls) -> argparse.ArgumentParser:
        if cls.__doc__ is None:
            raise RuntimeError(f'CLI app "{cls.__name__}" is not documented')

        # Patch help message width
        os.environ['COLUMNS'] = str(shutil.get_terminal_size(fallback=(100, 24)).columns)
        parser = argparse.ArgumentParser(description=Color.BOLD(cls.__doc__))

        action_parsers = parser.add_subparsers(dest='action', required=True)
        for sub_action in cls.get_class_cli_actions():
            action_parser = action_parsers.add_parser(
                sub_action.action_name,
                help=sub_action.__doc__,
                description=Color.BOLD(sub_action.__doc__))

            cls._setup_default_cli_options(action_parser)
            required_arguments = action_parser.add_argument_group(
                f'required arguments for {Color.BOLD(sub_action.action_name)}')
            optional_arguments = action_parser.add_argument_group(
                f'optional arguments for {Color.BOLD(sub_action.action_name)}')
            for argument in chain(cls._CLASS_ARGUMENTS, sub_action.arguments):
                argument_group = required_arguments if argument.is_required() else optional_arguments
                argument.register(argument_group)
        return parser

    def _obfuscate_command(self, command_args: Sequence[CommandArg],
                           obfuscate_patterns: Optional[Iterable[ObfuscationPattern]] = None) -> ObfuscatedCommand:

        all_obfuscate_patterns = set(chain((obfuscate_patterns or []), self.default_obfuscation))

        def should_obfuscate(arg: CommandArg):
            for pattern in all_obfuscate_patterns:
                if isinstance(pattern, re.Pattern):
                    match = pattern.match(str(arg)) is not None
                elif callable(pattern):
                    match = pattern(arg)
                elif isinstance(pattern, (str, bytes, pathlib.Path)):
                    match = pattern == arg
                else:
                    raise ValueError(f'Invalid obfuscation pattern {pattern}')
                if match:
                    return True
            return False

        def obfuscate_arg(arg: CommandArg):
            return self.obfuscation if should_obfuscate(arg) else shlex.quote(str(arg))

        return ObfuscatedCommand(' '.join(map(obfuscate_arg, command_args)))

    @classmethod
    def _expand_variables(cls, command_args: Sequence[CommandArg]) -> List[str]:
        def expand(command_arg: CommandArg):
            expanded = os.path.expanduser(os.path.expandvars(command_arg))
            if isinstance(expanded, bytes):
                return expanded.decode()
            return expanded

        return [expand(command_arg) for command_arg in command_args]

    def execute(self, command_args: Sequence[CommandArg],
                obfuscate_patterns: Optional[Sequence[ObfuscationPattern]] = None,
                show_output: bool = True) -> CliProcess:
        return CliProcess(
            command_args,
            self._obfuscate_command(command_args, obfuscate_patterns),
            dry=self.dry_run,
            print_streams=show_output
        ).execute()


def action(action_name: str, *arguments: Argument):
    """
    Decorator to mark that the method is usable from CLI
    :param action_name: Name of the CLI parameter
    :param arguments: CLI arguments that are required for this method to work
    """

    def decorator(func):
        if func.__doc__ is None:
            raise RuntimeError(f'Action "{action_name}" defined by {func} is not documented')
        func.is_cli_action = True
        func.action_name = action_name
        func.arguments = arguments

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def common_arguments(*class_arguments: Argument):
    """
    Decorator to mark that the method is usable from CLI
    :param class_arguments: CLI arguments that are required to initialize the class
    """

    def decorator(cli_app_type):
        if not issubclass(cli_app_type, CliApp):
            raise RuntimeError(f'Cannot decorate {cli_app_type} with {common_arguments}')
        if class_arguments:
            cli_app_type._CLASS_ARGUMENTS = tuple(class_arguments)
        return cli_app_type

    return decorator
