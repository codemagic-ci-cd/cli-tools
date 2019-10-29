#!/usr/bin/env python3

from __future__ import annotations

import abc
import argparse
import logging
import os
import pathlib
import shlex
import subprocess
import sys
import time
from functools import wraps
from itertools import chain
from typing import Optional, Sequence, Iterable, Type, Tuple, List, Union, AnyStr, NewType

from .argument import Argument, ActionCallable

CommandArg = Union[AnyStr, pathlib.Path]
ObfuscatedCommand = NewType('ObfuscatedCommand', str)


class CliAppException(Exception):

    def __init__(self, command: ObfuscatedCommand, message: str, returncode: int):
        self.command = command
        self.message = message
        self.returncode = returncode

    def __str__(self):
        return f'Running {self.command} failed with exit code {self.returncode}: {self.message}'


class CliApp(metaclass=abc.ABCMeta):
    CLI_EXCEPTION_TYPE: Type[CliAppException] = CliAppException

    def __init__(self, dry=False):
        self.dry_run = dry
        self.default_obfuscation = []
        self.obfuscation = 8 * '*'
        self.logger = logging.getLogger(self.__class__.__name__)

    @classmethod
    def from_cli_args(cls, cli_args: argparse.Namespace):
        return cls()

    @classmethod
    def _handle_cli_exception(cls, cli_exception: CliAppException):
        sys.stderr.write(f'{cli_exception.message}\n')
        sys.exit(cli_exception.returncode)

    @classmethod
    def invoke_cli(cls):
        args = CliApp.setup_cli(cls)
        instance = cls.from_cli_args(args)
        cli_action = {ac.action_name: ac for ac in instance.get_cli_actions()}[args.action]
        try:
            cli_action(**Argument.get_action_kwargs(cli_action, args))
        except cls.CLI_EXCEPTION_TYPE as cli_exception:
            cls._handle_cli_exception(cli_exception)

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
    def _enable_logging(cls):
        # TODO: enable logging only for some CLI arg?
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s > %(message)s', '%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        logger = logging.getLogger()
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    @classmethod
    def setup_cli(cls, command_executor_type: Type[CliApp]) -> argparse.Namespace:
        cls._enable_logging()
        parser = argparse.ArgumentParser(description=command_executor_type.__doc__)

        action_parsers = parser.add_subparsers(dest='action')
        for sub_action in command_executor_type.get_class_cli_actions():
            action_parser = action_parsers.add_parser(
                sub_action.action_name,
                help=sub_action.__doc__,
                description=sub_action.__doc__)
            for argument_type in sub_action.required_arguments:
                argument_type.add_to_parser(action_parser)

        args = parser.parse_args()

        if not args.action:
            parser.print_help()
            sys.exit(0)

        return args

    def _obfuscate_command(self,
                           command_args: Sequence[CommandArg],
                           obfuscate_args: Optional[Iterable[CommandArg]] = None) -> ObfuscatedCommand:
        # TODO: support regex expressions for matching
        obfuscate_args = set(chain((obfuscate_args or []), self.default_obfuscation))
        obfuscated = ' '.join(
            self.obfuscation if arg in obfuscate_args else shlex.quote(str(arg))
            for arg in command_args)
        return ObfuscatedCommand(obfuscated)

    @classmethod
    def _expand_variables(cls, command_args: Sequence[CommandArg]) -> List[str]:
        def expand(command_arg: CommandArg):
            expanded = os.path.expanduser(os.path.expandvars(command_arg))
            if isinstance(expanded, bytes):
                return expanded.decode()
            return expanded

        return [expand(command_arg) for command_arg in command_args]

    def execute(self,
                command_args: Sequence[CommandArg],
                obfuscate_args: Optional[Sequence[CommandArg]] = None
                ) -> Tuple[subprocess.Popen, ObfuscatedCommand]:
        obfuscated_command = self._obfuscate_command(command_args, obfuscate_args)
        start = time.time()

        if self.dry_run:
            self.logger.info(f'Skip executing {obfuscated_command} due to dry run')
            process = subprocess.Popen(['echo', 'skip'])
            process.communicate()
        else:
            self.logger.info(f'Execute "{obfuscated_command}"')
            process = subprocess.Popen(self._expand_variables(command_args))
            process.communicate()
            self.logger.info(
                f'Completed "{obfuscated_command}" with returncode {process.returncode} in {time.time() - start:.2f}')

        return process, obfuscated_command


def action(action_name: str, *arguments: Argument, optional_arguments=tuple()):
    """
    Decorator to mark that the method is usable form CLI
    :param action_name: Name of the CLI parameter
    :param arguments: CLI arguments that are required for this method to work
    :param optional_arguments: CLI arguments that can be omitted
    """

    def decorator(func):
        func.is_cli_action = True
        func.action_name = action_name
        func.required_arguments = arguments
        func.optionals = optional_arguments

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator
