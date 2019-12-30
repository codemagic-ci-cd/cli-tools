from __future__ import annotations

import enum
import re
import sys
from functools import reduce
from typing import Optional
from typing import overload


class Colors(enum.Enum):
    RESET = '\033[0m'
    BOLD = '\033[01m'
    ITALIC = '\033[03m'
    UNDERLINE = '\033[04m'
    STRIKE = '\033[09m'
    RED = '\033[31m'
    RED_BG = '\033[41m'
    GREEN = '\033[32m'
    GREEN_BG = '\033[42m'
    YELLOW = '\033[33m'
    YELLOW_BG = '\033[43m'
    BLUE = '\033[34m'
    BLUE_BG = '\033[44m'
    MAGENTA = '\033[35m'
    MAGENTA_BG = '\033[45m'
    CYAN = '\033[36m'
    CYAN_BG = '\033[46m'
    WHITE = '\033[37m'
    WHITE_BG = '\033[47m'
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_BLACK_BG = '\033[100m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_RED_BG = '\033[101m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_GREEN_BG = '\033[102m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_YELLOW_BG = '\033[103m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_BLUE_BG = '\033[104m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_MAGENTA_BG = '\033[105m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_CYAN_BG = '\033[106m'
    BRIGHT_WHITE = '\033[97m'
    BRIGHT_WHITE_BG = '\033[107m'

    @overload
    def __call__(self, string: None) -> None:
        ...

    @overload
    def __call__(self, string: str) -> str:
        ...

    def __call__(self, string: Optional[str]):
        if string is None:
            return None
        if '--no-color' in sys.argv:
            colored = string
        else:
            patt = re.compile(r'^(\s*)(.*)(\s*)$', flags=re.MULTILINE)
            colored = patt.sub(r'\1%s\2%s\3' % (self.value, Colors.RESET.value), string)
        return colored

    @classmethod
    def apply(cls, string: str, *colors: Colors) -> str:
        return reduce(lambda s, color: color(s), colors, string)

    @classmethod
    def remove(cls, string: str) -> str:
        start = '|'.join(re.escape(color.value) for color in Colors)
        no_match = ''.join(re.escape(color.value) for color in Colors)
        end = re.escape(Colors.RESET.value)
        patt = re.compile(f'({start})([^{no_match}]+)({end})')
        if not patt.search(string):
            return string
        return cls.remove(patt.sub(r'\2', string))


if __name__ == '__main__':
    styles = [
        Colors.GREEN,
        Colors.BOLD,
        Colors.ITALIC,
        Colors.STRIKE,
        Colors.BRIGHT_BLACK_BG
    ]
    print(Colors.apply(' '.join(s.name for s in styles), *styles))
    for c in Colors:
        print(c(c.name))
