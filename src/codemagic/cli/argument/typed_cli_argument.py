#!/usr/bin/env python3
from __future__ import annotations

import abc
import argparse
import os
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Callable
from typing import Generic
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import Union

from codemagic.cli.colors import Colors

from .argument_formatter import ArgumentFormatter

if TYPE_CHECKING:
    from .argument_properties import ArgumentProperties

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
    def get_description(cls, properties: 'ArgumentProperties') -> str:
        description = f'{properties.description.rstrip(".")}.'
        if cls.environment_variable_key is not None:
            description += '\nIf not given, the value will be checked from ' \
                           f'environment variable {Colors.CYAN(cls.environment_variable_key)}.'
        return description

    @classmethod
    def get_missing_value_error_message(cls, properties: 'ArgumentProperties') -> str:
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
    def get_description(cls, properties: 'ArgumentProperties') -> str:
        description = super().get_description(properties)
        usage = f'Alternatively to entering {Colors.CYAN(properties.key.upper())} in plaintext, ' \
                f'it may also be specified using a "@env:" prefix followed by a environment variable name, ' \
                f'or "@file:" prefix followed by a path to the file containing the value.'
        example = 'Example: "@env:<variable>" uses the value in the environment variable named "<variable>", ' \
                  'and "@file:<file_path>" uses the value from file at "<file_path>".'
        try:
            default_value = (properties.argparse_kwargs or {})['default']
            default = ArgumentFormatter.format_default_value(default_value)
            return '\n'.join([description, usage, example, default])
        except KeyError:
            return '\n'.join([description, usage, example])

    def __str__(self):
        return self._raw_value

    def __repr__(self):
        return self._raw_value
