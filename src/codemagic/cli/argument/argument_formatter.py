#!/usr/bin/env python3
from __future__ import annotations

import shlex
from typing import Any

from codemagic.cli.colors import Colors


class ArgumentFormatter:

    @classmethod
    def format_default_value(cls, default_value: Any) -> str:
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
