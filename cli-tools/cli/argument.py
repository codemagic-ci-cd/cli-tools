#!/usr/bin/env python3
from __future__ import annotations

import argparse
import enum
from typing import Type, Tuple, NamedTuple, Dict, Optional, Sequence


class ActionCallable:
    def __call__(self, *args, **kwargs):
        pass

    is_cli_action: bool
    action_name: str
    required_arguments: Sequence[Argument]


class ArgumentValue(NamedTuple):
    key: str
    description: str
    type: Type = str
    flags: Tuple[str, ...] = tuple()
    argparse_kwargs: Optional[Dict[str, object]] = None
    is_action_kwarg: bool = False


class Argument(ArgumentValue, enum.Enum):

    def register(self, argument_group: argparse._ArgumentGroup):
        argument_group.add_argument(
            *self.value.flags,
            type=self.value.type,
            help=self.value.description,
            dest=self.value.key,
            **(self.value.argparse_kwargs or {}))

    def is_required(self):
        return (self.value.argparse_kwargs or {}).get('required', True)

    def get_default(self):
        return (self.value.argparse_kwargs or {}).get('default', None)

    @classmethod
    def get_action_kwargs(cls, cli_action: ActionCallable, cli_args: argparse.Namespace) -> Dict[str, object]:
        return {
            arg_type.value.key: getattr(cli_args, arg_type.value.key, arg_type.get_default())
            for arg_type in cli_action.required_arguments
            if arg_type.value.is_action_kwarg
        }
