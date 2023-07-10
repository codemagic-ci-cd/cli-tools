#!/usr/bin/env python3

from __future__ import annotations

import pathlib
from typing import AnyStr
from typing import Callable
from typing import NewType
from typing import Pattern
from typing import Union

CommandArg = Union[AnyStr, pathlib.Path]
ObfuscationPattern = Union[Pattern, Callable[[CommandArg], bool], CommandArg]
ObfuscatedCommand = NewType("ObfuscatedCommand", str)
