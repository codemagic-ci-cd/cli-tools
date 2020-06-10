#!/usr/bin/env python3

from __future__ import annotations

import abc
import argparse
import os
import pathlib
import platform
import re
import shlex
import shutil
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

from codemagic import __version__
from codemagic.utilities import log
from .argument import ActionCallable
from .argument import Argument
from .argument import ArgumentFormatter
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
    _printer = None

    def __init__(self, dry=False, verbose=False, **cli_options):
        self.dry_run = dry
        self.default_obfuscation = []
        self.obfuscation = 8 * '*'
        self.verbose = verbose
        self.logger = log.get_logger(self.__class__)

    @classmethod
    def get_executable_name(cls) -> str:
        return re.sub(r'(.)([A-Z])', r'\1-\2', cls.__name__).lower()

    @classmethod
    def echo(cls, message: str, *args, **kwargs):
        """
        Log given message to the STDOUT without any extra logging formatting
        and log the message to the the logfile with proper formatting.
        """
        if cls._printer is None:
            cls._printer = log.get_printer(cls)
        cls._printer.info(message, *args, **kwargs)

    @classmethod
    def from_cli_args(cls, cli_args: argparse.Namespace) -> CliApp:
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
    def _handle_generic_exception(cls, action_name: str) -> int:
        logger = log.get_logger(cls)
        message = (
            f'Executing {cls.__name__} action {action_name} failed unexpectedly. '
            f'Detailed logs are available at "{log.get_log_path()}". '
            f'To see more details about the error, add `--verbose` command line option.'
        )
        logger.warning(Colors.RED(message))
        file_logger = log.get_file_logger(cls)
        file_logger.exception('Exception traceback:')
        return 9

    @classmethod
    def _handle_cli_exception(cls, cli_exception: CliAppException) -> int:
        logger = log.get_logger(cls)
        logger.error(f'{Colors.RED(cli_exception.message)}')
        if cli_exception.cli_process:
            return cli_exception.cli_process.returncode
        else:
            return 1

    @classmethod
    def _create_instance(cls, parser: argparse.ArgumentParser, cli_args: argparse.Namespace) -> CliApp:
        try:
            instance = cls.from_cli_args(cli_args)
        except argparse.ArgumentError as argument_error:
            parser.error(str(argument_error))
            raise

        instance.verbose = cli_args.verbose
        return instance

    def _invoke_action(self, args: argparse.Namespace):
        actions = self.get_cli_actions()
        cli_action = {ac.action_name: ac for ac in actions}[args.action]
        action_args = {
            arg_type.value.key: arg_type.from_args(args, arg_type.get_default())
            for arg_type in cli_action.arguments
        }
        return cli_action(**action_args)

    @classmethod
    def show_version(cls):
        executable = cls.get_executable_name()
        cls.echo(f'{cls.__name__} installed at {shutil.which(executable) or executable}')
        cls.echo(f'{executable} {__version__}')
        return __version__

    @classmethod
    def is_cli_invocation(cls) -> bool:
        return os.environ.get('_CLI_INVOCATION') == 'true'

    @classmethod
    def invoke_cli(cls) -> NoReturn:
        os.environ['_CLI_INVOCATION'] = 'true'
        parser = cls._setup_cli_options()
        args = parser.parse_args()
        cls._setup_logging(args)

        cls._log_cli_invoke_started()
        started_at = time.time()
        status = 0
        try:
            if args.show_version:
                cls.show_version()
            elif args.action:
                app = cls._create_instance(parser, args)
                app._invoke_action(args)
            else:
                raise argparse.ArgumentError(args.action, 'the following argument is required: action')
        except argparse.ArgumentError as argument_error:
            parser.error(str(argument_error))
            status = 2
        except cls.CLI_EXCEPTION_TYPE as cli_exception:
            status = cls._handle_cli_exception(cli_exception)
        except KeyboardInterrupt:
            logger = log.get_logger(cls)
            logger.warning(Colors.YELLOW('Terminated'))
            status = 130
        except Exception:
            status = cls._handle_generic_exception(args.action)
        finally:
            cls._log_cli_invoke_completed(args.action, started_at, status)
        sys.exit(status)

    @classmethod
    def _log_cli_invoke_started(cls):
        exec_line = f'Execute {" ".join(map(shlex.quote, sys.argv))}'
        install_line = f'From {pathlib.Path(__file__).parent.parent.resolve()}'
        version_line = f'Using Python {platform.python_version()} on {platform.system()} {platform.release()}'
        separator = '-' * max(len(exec_line), len(version_line), len(install_line))
        file_logger = log.get_file_logger(cls)
        file_logger.debug(Colors.MAGENTA(separator))
        file_logger.debug(Colors.MAGENTA(exec_line))
        file_logger.debug(Colors.MAGENTA(install_line))
        file_logger.debug(Colors.MAGENTA(version_line))
        file_logger.debug(Colors.MAGENTA(separator))

    @classmethod
    def _log_cli_invoke_completed(cls, action_name: str, started_at: float, exit_status: int):
        seconds = int(time.time() - started_at)
        duration = time.strftime("%M:%S", time.gmtime(seconds))
        msg = f'Completed {cls.__name__} {action_name} in {duration} with status code {exit_status}'
        file_logger = log.get_file_logger(cls)
        file_logger.debug(Colors.MAGENTA('-' * len(msg)))
        file_logger.debug(Colors.MAGENTA(msg))
        file_logger.debug(Colors.MAGENTA('-' * len(msg)))

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
        log.initialize_logging(
            stream={'stderr': sys.stderr, 'stdout': sys.stdout}[cli_args.log_stream],
            verbose=cli_args.verbose,
            enable_logging=cli_args.enable_logging
        )

    @classmethod
    def get_default_cli_options(cls, cli_options_parser):
        options_group = cli_options_parser.add_argument_group(Colors.UNDERLINE('Options'))
        options_group.add_argument('--log-stream', type=str, default='stderr', choices=['stderr', 'stdout'],
                                   help=f'Log output stream. {ArgumentFormatter.format_default_value("stderr")}')
        options_group.add_argument('--no-color', dest='no_color', action='store_true',
                                   help='Do not use ANSI colors to format terminal output')
        options_group.add_argument('--version', dest='show_version', action='store_true',
                                   help='Show tool version and exit')
        options_group.add_argument('-s', '--silent', dest='enable_logging', action='store_false',
                                   help='Disable log output for commands')
        options_group.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                                   help='Enable verbose logging for commands')

        options_group.set_defaults(
            enable_logging=True,
            no_color=False,
            show_version=False,
            verbose=False,
        )

    @classmethod
    def _setup_class_cli_options(cls, cli_options_parser):
        executable = cli_options_parser.prog.split()[0]
        tool_required_arguments = cli_options_parser.add_argument_group(
            Colors.UNDERLINE(f'Required arguments for {Colors.BOLD(executable)}'))
        tool_optional_arguments = cli_options_parser.add_argument_group(
            Colors.UNDERLINE(f'Optional arguments for {Colors.BOLD(executable)}'))
        for argument in cls.CLASS_ARGUMENTS:
            argument_group = tool_required_arguments if argument.is_required() else tool_optional_arguments
            argument.register(argument_group)

    @classmethod
    def _setup_cli_options(cls) -> argparse.ArgumentParser:
        if cls.__doc__ is None:
            raise RuntimeError(f'CLI app "{cls.__name__}" is not documented')

        parser = argparse.ArgumentParser(description=Colors.BOLD(cls.__doc__), formatter_class=CliHelpFormatter)
        cls.get_default_cli_options(parser)

        actions_title = Colors.BOLD(Colors.UNDERLINE('Available commands'))
        action_parsers = parser.add_subparsers(dest='action', title=actions_title)

        for sub_action in cls.get_class_cli_actions():
            action_parser = action_parsers.add_parser(
                sub_action.action_name,
                formatter_class=CliHelpFormatter,
                help=sub_action.__doc__,
                description=Colors.BOLD(sub_action.__doc__))

            cls.get_default_cli_options(action_parser)
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
