#!/usr/bin/env python3

from __future__ import annotations

import pathlib
from typing import Union, AnyStr, NewType, Callable, Pattern

CommandArg = Union[AnyStr, pathlib.Path]
ObfuscationPattern = Union[Pattern, Callable[[CommandArg], bool], CommandArg]
ObfuscatedCommand = NewType('ObfuscatedCommand', str)
