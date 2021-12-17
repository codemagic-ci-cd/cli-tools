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
    default_value: Optional[T] = None

    def __init__(self, raw_value: str, from_environment=False):
        self._raw_value = raw_value
        self.value: T = self._parse_value()
        self._from_environment = from_environment

    @classmethod
    def resolve_value(cls, argument_instance: Optional[Union[T, TypedCliArgument]]) -> T:
        """
        Resolve variable value from either typed argument or literal value, or
        return the default value defined for the typed argument in case no argument
        instance is available.
        This is a workaround to support overriding default value by environment variable.
        """
        if argument_instance is not None:
            if isinstance(argument_instance, cls):
                return argument_instance.value
            else:
                return argument_instance  # type: ignore
        assert cls.default_value is not None
        return cls.default_value

    @classmethod
    def from_environment_variable_default(cls) -> Optional['TypedCliArgument[T]']:
        if cls.environment_variable_key is None:
            return None
        elif cls.environment_variable_key not in os.environ:
            return None
        try:
            return cls(os.environ[cls.environment_variable_key], from_environment=True)
        except argparse.ArgumentTypeError as ate:
            raise ValueError(str(ate)) from ate

    @classmethod
    def _is_valid(cls, value: T) -> bool:
        return bool(value)

    @classmethod
    def _apply_type(cls, non_typed_value: str) -> T:
        value = cls.argument_type(non_typed_value)
        if not cls._is_valid(value):
            raise argparse.ArgumentTypeError(f'Provided value "{value}" is not valid')
        return value

    def _parse_value(self) -> T:
        value = self._raw_value
        return self._apply_type(value)

    @classmethod
    def get_description(cls, properties: 'ArgumentProperties', include_default=True) -> str:
        description = f'{properties.description.rstrip(".")}.'
        if cls.environment_variable_key is not None:
            description += '\nIf not given, the value will be checked from the ' \
                           f'environment variable {Colors.CYAN(cls.environment_variable_key)}.'
        if include_default:
            try:
                if cls.default_value:
                    default_value = cls.default_value
                else:
                    default_value = (properties.argparse_kwargs or {})['default']
            except KeyError:
                pass
            else:
                default = ArgumentFormatter.format_default_value(default_value)
                return '\n'.join([description, default])
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
        except argparse.ArgumentTypeError as ate:
            error_message = f'Provided value in environment variable "{key}" is not valid. {ate}'
            raise argparse.ArgumentTypeError(error_message) from ate

    def _get_from_file(self) -> T:
        path = Path(self._raw_value[6:])
        if not path.exists():
            raise argparse.ArgumentTypeError(f'File "{path}" does not exist')
        if not path.is_file():
            raise argparse.ArgumentTypeError(f'"{path}" is not a file')
        content = path.read_text()
        try:
            return self._apply_type(content)
        except argparse.ArgumentTypeError as ate:
            error_message = f'Provided value in file "{path}" is not valid. {ate}'
            raise argparse.ArgumentTypeError(error_message) from ate

    def _parse_value(self) -> T:
        if self._is_from_environment():
            return self._get_from_environment()
        elif self._is_from_file():
            return self._get_from_file()
        else:
            return super()._parse_value()

    @classmethod
    def get_description(cls, properties: 'ArgumentProperties', include_default=True) -> str:
        description = super().get_description(properties, include_default=False)
        usage = f'Alternatively to entering {Colors.CYAN(properties.key.upper())} in plaintext, ' \
                f'it may also be specified using the "{Colors.WHITE("@env:")}" prefix followed ' \
                f'by an environment variable name, or the "{Colors.WHITE("@file:")}" prefix followed ' \
                f'by a path to the file containing the value.'
        example = f'Example: "{Colors.WHITE("@env:<variable>")}" uses the value in the environment variable ' \
                  f'named "{Colors.WHITE("<variable>")}", and "{Colors.WHITE("@file:<file_path>")}" ' \
                  f'uses the value from the file at "{Colors.WHITE("<file_path>")}".'

        if include_default:
            try:
                default_value = (properties.argparse_kwargs or {})['default']
            except KeyError:
                pass
            else:
                default = ArgumentFormatter.format_default_value(default_value)
                return '\n'.join([description, usage, example, default])
        return '\n'.join([description, usage, example])

    def __str__(self):
        return self._raw_value

    def __repr__(self):
        return self._raw_value
