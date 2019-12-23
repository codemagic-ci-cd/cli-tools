#!/usr/bin/env python3

from __future__ import annotations

import abc
import argparse
import logging
import os
import pathlib
import re
import shlex
import sys
import time
from functools import wraps
from itertools import chain
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import NoReturn
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Type

from .argument import ActionCallable
from .argument import Argument
from .cli_help_formatter import CliHelpFormatter
from .cli_process import CliProcess
from .cli_types import CommandArg
from .cli_types import ObfuscatedCommand
from .cli_types import ObfuscationPattern
from .colors import Colors


class CliAppException(Exception):

    def __init__(self, message: str, cli_process: Optional[CliProcess] = None):
        self.cli_process = cli_process
        self.message = message

    def __str__(self):
        if not self.cli_process:
            return self.message
        return (
            f'Running {self.cli_process.safe_form} failed with '
            f'exit code {self.cli_process.returncode}: {self.message}'
        )


class CliApp(metaclass=abc.ABCMeta):
    CLASS_ARGUMENTS: Tuple[Argument, ...] = tuple()
    REGISTERED_CLASS_ARGUMENTS: Dict[Type[CliApp], Tuple[Argument, ...]] = {}
    CLI_EXCEPTION_TYPE: Type[CliAppException] = CliAppException

    def __init__(self, dry=False, verbose=False, **cli_options):
        self.dry_run = dry
        self.default_obfuscation = []
        self.obfuscation = 8 * '*'
        self.verbose = verbose
        self.logger = logging.getLogger(self.__class__.__name__)

    @classmethod
    def from_cli_args(cls, cli_args: argparse.Namespace) -> 'CliApp':
        return cls(**{argument.value.key: argument.from_args(cli_args) for argument in cls.CLASS_ARGUMENTS})

    @classmethod
    def _parent_class_kwargs(cls, cli_args: argparse.Namespace) -> Dict[str, Any]:
        class_args = cls.REGISTERED_CLASS_ARGUMENTS[cls]
        class_arg_keys = {arg.key for arg in class_args}
        return {
            key: value for key, value in cli_args.__dict__.items()
            if key not in class_arg_keys
        }

    @classmethod
    def _handle_cli_exception(cls, cli_exception: CliAppException) -> int:
        logger = logging.getLogger(cls.__name__)
        logger.error(f'{Colors.RED(cli_exception.message)}')
        if cli_exception.cli_process:
            return cli_exception.cli_process.returncode
        else:
            return 1

    @classmethod
    def invoke_cli(cls) -> NoReturn:
        parser = cls._setup_cli_options()
        args = parser.parse_args()
        logger = cls._setup_logging(args)

        try:
            instance = cls.from_cli_args(args)
            instance.verbose = args.verbose
        except argparse.ArgumentError as argument_error:
            parser.error(str(argument_error))

        cli_action = {ac.action_name: ac for ac in instance.get_cli_actions()}[args.action]
        action_args = {
            arg_type.value.key: arg_type.from_args(args, arg_type.get_default())
            for arg_type in cli_action.arguments
        }
        start = time.time()
        try:
            cli_action(**action_args)
            status = 0
        except argparse.ArgumentError as argument_error:
            parser.error(str(argument_error))
            status = 2
        except cls.CLI_EXCEPTION_TYPE as cli_exception:
            status = cls._handle_cli_exception(cli_exception)
        except KeyboardInterrupt:
            logger.warning(Colors.YELLOW('Terminated'))
            status = 130
        finally:
            seconds = int(time.time() - start)
            logger.debug(f'Completed in {time.strftime("%M:%S", time.gmtime(seconds))}.')
        sys.exit(status)

    @classmethod
    def get_class_cli_actions(cls) -> Iterable[ActionCallable]:
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if callable(attr) and getattr(attr, 'is_cli_action', False):
                yield attr

    def get_cli_actions(self) -> Iterable[ActionCallable]:
        for class_action in self.get_class_cli_actions():
            yield getattr(self, class_action.__name__)

    @classmethod
    def _setup_logging(cls, cli_args: argparse.Namespace):
        stream = {'stderr': sys.stderr, 'stdout': sys.stdout}[cli_args.log_stream]
        if cli_args.verbose:
            log_fmt = '[%(asctime)s] %(levelname)-5s > %(message)s'
            log_level = logging.DEBUG
        elif not cli_args.enable_logging:
            log_fmt = '%(message)s'
            log_level = logging.ERROR
        else:
            log_fmt = '%(message)s'
            log_level = logging.INFO

        formatter = logging.Formatter(log_fmt, '%m-%d %H:%M:%S')
        handler = logging.StreamHandler(stream)
        handler.setLevel(log_level)
        handler.setFormatter(formatter)

        logger = logging.getLogger()
        logger.addHandler(handler)
        logger.setLevel(log_level)
        return logger

    @classmethod
    def _setup_default_cli_options(cls, cli_options_parser):
        options_group = cli_options_parser.add_argument_group(Colors.UNDERLINE('Options'))
        options_group.add_argument('-s', '--silent', dest='enable_logging', action='store_false',
                                   help='Disable log output for commands')
        options_group.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                                   help='Enable verbose logging for commands')
        options_group.add_argument('--no-color', dest='no_color', action='store_true',
                                   help='Do not use ANSI colors to format terminal output')
        options_group.add_argument('--log-stream', type=str, default='stderr', choices=['stderr', 'stdout'],
                                   help=f'Log output stream. {Argument.format_default("stderr")}')

        options_group.set_defaults(
            enable_logging=True,
            verbose=False,
            no_color=False,
        )

    @classmethod
    def _setup_class_cli_options(cls, cli_options_parser):
        executable = cli_options_parser.prog.split()[0]
        tool_required_arguments = cli_options_parser.add_argument_group(
            cls.fmt(f'Required arguments for {Colors.BOLD(executable)}'))
        tool_optional_arguments = cli_options_parser.add_argument_group(
            cls.fmt(f'Optional arguments for {Colors.BOLD(executable)}'))
        for argument in cls.CLASS_ARGUMENTS:
            argument_group = tool_required_arguments if argument.is_required() else tool_optional_arguments
            argument.register(argument_group)

    @classmethod
    def _setup_cli_options(cls) -> argparse.ArgumentParser:
        if cls.__doc__ is None:
            raise RuntimeError(f'CLI app "{cls.__name__}" is not documented')

        parser = argparse.ArgumentParser(description=Colors.BOLD(cls.__doc__), formatter_class=CliHelpFormatter)
        cls._setup_default_cli_options(parser)

        action_parsers = parser.add_subparsers(
            dest='action',
            required=True,
            title=Colors.BOLD(Colors.UNDERLINE('Available commands'))
        )
        for sub_action in cls.get_class_cli_actions():
            action_parser = action_parsers.add_parser(
                sub_action.action_name,
                formatter_class=CliHelpFormatter,
                help=sub_action.__doc__,
                description=Colors.BOLD(sub_action.__doc__))

            cls._setup_default_cli_options(action_parser)
            required_arguments = action_parser.add_argument_group(
                Colors.UNDERLINE(f'Required arguments for command {Colors.BOLD(sub_action.action_name)}'))
            optional_arguments = action_parser.add_argument_group(
                Colors.UNDERLINE(f'Optional arguments for command {Colors.BOLD(sub_action.action_name)}'))
            for argument in sub_action.arguments:
                argument_group = required_arguments if argument.is_required() else optional_arguments
                argument.register(argument_group)
            cls._setup_class_cli_options(action_parser)
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
            print_streams=show_output or self.verbose
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

    def decorator(cli_app_type: Type[CliApp]):
        if not issubclass(cli_app_type, CliApp):
            raise RuntimeError(f'Cannot decorate {cli_app_type} with {common_arguments}')
        for class_argument in class_arguments:
            if not isinstance(class_argument, Argument):
                raise TypeError(f'Invalid argument to common_arguments: {class_argument}')
            elif class_argument in cli_app_type.CLASS_ARGUMENTS:
                raise ValueError(f'{class_argument} is already registered on class {cli_app_type.__name__}')
            else:
                cli_app_type.CLASS_ARGUMENTS += (class_argument,)

        cli_app_type.REGISTERED_CLASS_ARGUMENTS[cli_app_type] = tuple(class_arguments)
        return cli_app_type

    return decorator
