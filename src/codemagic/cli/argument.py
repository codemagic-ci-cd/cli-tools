#!/usr/bin/env python3
from __future__ import annotations

import argparse
import enum
import os
import types
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    NamedTuple,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)


class ActionCallable:
    def __call__(self, *args, **kwargs):
        pass

    is_cli_action: bool
    action_name: str
    arguments: Sequence[Argument]


class EnumArgumentValue(enum.Enum):

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.name.lower()


class EnvironmentArgumentValue:

    def __init__(self, raw_value: str):
        self._raw_value = raw_value
        self.value = self._parse_value()

    @classmethod
    def _is_valid(cls, value: str) -> bool:
        return bool(value)

    def _is_from_environment(self) -> bool:
        return self._raw_value.startswith('@env:')

    def _is_from_file(self) -> bool:
        return self._raw_value.startswith('@file:')

    def _get_from_environment(self) -> str:
        key = self._raw_value[5:]
        try:
            return os.environ[key]
        except KeyError:
            raise argparse.ArgumentTypeError(f'Environment variable "{key}" is not defined')

    def _get_from_file(self) -> str:
        path = Path(self._raw_value[6:])
        if not path.exists():
            raise argparse.ArgumentTypeError(f'File "{path}" does not exist')
        if not path.is_file():
            raise argparse.ArgumentTypeError(f'"{path}" is not a file')
        return path.read_text()[:-1]  # Strip the added newline character from the end

    def _parse_value(self) -> str:
        if self._is_from_environment():
            value = self._get_from_environment()
        elif self._is_from_file():
            value = self._get_from_file()
        else:
            value = self._raw_value
        if not self._is_valid(value):
            raise argparse.ArgumentTypeError('Provided value is not valid')
        return value

    @classmethod
    def get_description(cls, properties: ArgumentProperties) -> str:
        description = f'{properties.description.rstrip(".")}.'
        usage = f'Alternatively to entering "<{properties.key}>" in plaintext, ' \
            f'it may also be specified using a "@env:" prefix followed by a environment variable name, ' \
            f'or "@file:" prefix followed by a path to the file containing the value.'
        example = 'Example: "@env:<variable>" uses the value in the environment variable named "<variable>", ' \
                  'and "@env:<file_path>" uses the value from file at "<file_path>".'
        try:
            default = (properties.argparse_kwargs or {})['default']
            return '\n'.join([description, usage, example, f'[Default: {repr(default)}]'])
        except KeyError:
            return '\n'.join([description, usage, example])

    def __str__(self):
        return self._raw_value

    def __repr__(self):
        return self._raw_value


class ArgumentProperties(NamedTuple):
    key: str
    description: str
    type: Union[Type, Callable[[str], Any]] = str
    flags: Tuple[str, ...] = tuple()
    argparse_kwargs: Optional[Dict[str, object]] = None

    @property
    def _parser_argument(self):
        return getattr(self, '__parser_argument')

    @_parser_argument.setter
    def _parser_argument(self, parser_argument):
        setattr(self, '__parser_argument', parser_argument)

    def raise_argument_error(self, message):
        """
        :param message: ArgumentError message
        :raises: argparse.ArgumentError
        """
        raise argparse.ArgumentError(self._parser_argument, message)

    def from_args(self, cli_args: argparse.Namespace, default=None):
        return vars(cli_args)[self.key] or default

    def get_description(self):
        description = self.description
        try:
            default = (self.argparse_kwargs or {})['default']
            if isinstance(default, (Path, str)):
                description = f'{description} [Default: "{default}"]'
            elif default is not None:
                description = f'{description} [Default: {default}]'
        except KeyError:
            pass

        if isinstance(self.type, (types.FunctionType, types.MethodType)):
            return description
        elif issubclass(self.type, EnvironmentArgumentValue):
            return self.type.get_description(self)
        else:
            return description


class Argument(ArgumentProperties, enum.Enum):

    def register(self, argument_group: argparse._ArgumentGroup):
        kwargs = self.value.argparse_kwargs or {}
        if 'action' not in kwargs:
            kwargs['type'] = self.value.type
        self._parser_argument = argument_group.add_argument(
            *self.value.flags,
            help=self.value.get_description(),
            dest=self.value.key,
            **kwargs)

    def is_required(self):
        return (self.value.argparse_kwargs or {}).get('required', True)

    def get_default(self):
        return (self.value.argparse_kwargs or {}).get('default', None)
