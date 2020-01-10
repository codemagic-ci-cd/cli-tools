#!/usr/bin/env python3
from __future__ import annotations

import abc
import argparse
import enum
import inspect
import os
import shlex
import types
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Dict
from typing import Generic
from typing import NamedTuple
from typing import NoReturn
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union

from codemagic.cli.colors import Colors


class ActionCallable:
    is_cli_action: bool
    action_name: str
    arguments: Sequence[Argument]
    __name__: str
    __call__: Callable


T = TypeVar('T')


class TypedCliArgument(Generic[T], metaclass=abc.ABCMeta):
    argument_type: Union[Type[T], Callable[[str], T]] = str  # type: ignore
    environment_variable_key: Optional[str] = None

    def __init__(self, raw_value: str, from_environment=False):
        self._raw_value = raw_value
        self.value: T = self._parse_value()
        self._from_environment = from_environment

    @classmethod
    def from_environment_variable_default(cls) -> Optional['TypedCliArgument[T]']:
        if cls.environment_variable_key is None:
            return None
        elif cls.environment_variable_key not in os.environ:
            return None
        return cls(os.environ[cls.environment_variable_key], from_environment=True)

    @classmethod
    def _is_valid(cls, value: T) -> bool:
        return bool(value)

    @classmethod
    def _apply_type(cls, non_typed_value: str) -> T:
        value = cls.argument_type(non_typed_value)
        if not cls._is_valid(value):
            raise ValueError(f'Provided value "{value}" is not valid')
        return value

    def _parse_value(self) -> T:
        value = self._raw_value
        return self._apply_type(value)

    @classmethod
    def get_description(cls, properties: ArgumentProperties) -> str:
        description = f'{properties.description.rstrip(".")}.'
        if cls.environment_variable_key is not None:
            description += '\nIf not given, the value will be checked from ' \
                           f'environment variable {Colors.CYAN(cls.environment_variable_key)}.'
        return description

    @classmethod
    def get_missing_value_error_message(cls, properties: ArgumentProperties) -> str:
        name = Colors.CYAN(properties.key.upper())
        message = f'Missing value {name}. Provide it'
        if properties.flags:
            flags = Colors.BRIGHT_BLUE(','.join(properties.flags))
            message = f'{message} with argument {flags}'
        if cls.environment_variable_key:
            key = Colors.CYAN(cls.environment_variable_key)
            message = f'{message}, or set environment variable {key}'
        return message

    def __str__(self):
        if self._from_environment:
            return f'@env:{self.environment_variable_key}'
        return self._raw_value

    def __repr__(self):
        return repr(str(self))


class EnvironmentArgumentValue(TypedCliArgument[T], metaclass=abc.ABCMeta):

    def _is_from_environment(self) -> bool:
        return self._raw_value.startswith('@env:')

    def _is_from_file(self) -> bool:
        return self._raw_value.startswith('@file:')

    def _get_from_environment(self) -> T:
        key = self._raw_value[5:]
        try:
            return self._apply_type(os.environ[key])
        except KeyError:
            raise argparse.ArgumentTypeError(f'Environment variable "{key}" is not defined')

    def _get_from_file(self) -> T:
        path = Path(self._raw_value[6:])
        if not path.exists():
            raise argparse.ArgumentTypeError(f'File "{path}" does not exist')
        if not path.is_file():
            raise argparse.ArgumentTypeError(f'"{path}" is not a file')
        content = path.read_text()
        return self._apply_type(content)

    def _parse_value(self) -> T:
        if self._is_from_environment():
            return self._get_from_environment()
        elif self._is_from_file():
            return self._get_from_file()
        else:
            return super()._parse_value()

    @classmethod
    def get_description(cls, properties: ArgumentProperties) -> str:
        description = super().get_description(properties)
        usage = f'Alternatively to entering {Colors.CYAN(properties.key.upper())} in plaintext, ' \
                f'it may also be specified using a "@env:" prefix followed by a environment variable name, ' \
                f'or "@file:" prefix followed by a path to the file containing the value.'
        example = 'Example: "@env:<variable>" uses the value in the environment variable named "<variable>", ' \
                  'and "@file:<file_path>" uses the value from file at "<file_path>".'
        try:
            default_value = (properties.argparse_kwargs or {})['default']
            default = Argument.format_default(default_value)
            return '\n'.join([description, usage, example, default])
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


class Argument(ArgumentProperties, enum.Enum):

    def register(self, argument_group: argparse._ArgumentGroup):
        kwargs = self.value.argparse_kwargs or {}
        if 'action' not in kwargs:
            kwargs['type'] = self.value.type
        self._parser_argument = argument_group.add_argument(
            *self.value.flags,
            help=self.get_description(),
            dest=self.value.key,
            **kwargs)

    def is_required(self) -> bool:
        return (self.value.argparse_kwargs or {}).get('required', True)

    def get_default(self):
        return (self.value.argparse_kwargs or {}).get('default', None)

    def from_args(self, cli_args: argparse.Namespace, default=None):
        value = vars(cli_args)[self.value.key] or default
        if not value and \
                inspect.isclass(self.value.type) and \
                issubclass(self.value.type, TypedCliArgument):
            return self.value.type.from_environment_variable_default()
        return value

    @classmethod
    def format_default(cls, default_value: Any) -> str:
        try:
            if isinstance(default_value, str):
                raise TypeError
            iter(default_value)  # raises TypeError if not iterable
        except TypeError:
            escaped = shlex.quote(str(default_value))
        else:
            # Default value is iterable, use
            escaped = ' '.join(shlex.quote(str(v)) for v in default_value)
        return Colors.WHITE(f'[Default: {escaped}]')

    def get_description(self) -> str:
        description = self.value.description
        try:
            default_value = (self.value.argparse_kwargs or {})['default']
            if default_value is not None:
                description = f'{description} {self.format_default(default_value)}'
        except KeyError:
            pass

        if isinstance(self.value.type, (types.FunctionType, types.MethodType)):
            return description
        elif issubclass(self.value.type, TypedCliArgument):
            return self.value.type.get_description(self.value)
        else:
            return description

    def get_missing_value_error_message(self) -> str:
        if isinstance(self.value.type, (types.FunctionType, types.MethodType)):
            pass  # value.type is not a class and issubclass check would fail
        elif issubclass(self.value.type, TypedCliArgument):
            message = self.value.type.get_missing_value_error_message(self)
            if message:
                return message
        message = f'Value {Colors.CYAN(self.key.upper())} not provided'
        if self.flags:
            flags = ','.join(self.flags)
            message = f'{message} for {Colors.BRIGHT_BLUE(flags)}'
        return message

    def raise_argument_error(self, message: Optional[str] = None) -> NoReturn:
        """
        :param message: ArgumentError message
        :raises: argparse.ArgumentError
        """
        if message is None:
            message = self.get_missing_value_error_message()
        raise argparse.ArgumentError(self._parser_argument, message)
