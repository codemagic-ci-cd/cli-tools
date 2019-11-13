#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import re
from typing import Union, AnyStr, NewType, Callable

CommandArg = Union[AnyStr, pathlib.Path]
ObfuscationPattern = Union[re.Pattern, Callable[[CommandArg], bool], CommandArg]
ObfuscatedCommand = NewType('ObfuscatedCommand', str)
