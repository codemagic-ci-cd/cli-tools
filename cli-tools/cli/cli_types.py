#!/usr/bin/env python3

from __future__ import annotations

import pathlib
from typing import Union, AnyStr, NewType

CommandArg = Union[AnyStr, pathlib.Path]
ObfuscatedCommand = NewType('ObfuscatedCommand', str)
