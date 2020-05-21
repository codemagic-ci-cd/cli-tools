#!/usr/bin/env python3
from __future__ import annotations

import copy
from typing import Any
from typing import Callable
from typing import Dict
from typing import NamedTuple
from typing import Optional
from typing import Tuple
from typing import Type
from typing import Union


class ArgumentProperties(NamedTuple):
    key: str
    description: str
    type: Union[Type, Callable[[str], Any]] = str
    flags: Tuple[str, ...] = tuple()
    argparse_kwargs: Optional[Dict[str, object]] = None

    def duplicate(self, **overwrites) -> ArgumentProperties:
        kwargs = {}
        for field in self._fields:
            if field in overwrites:
                kwargs[field] = overwrites[field]
            else:
                kwargs[field] = copy.deepcopy(getattr(self, field))

        return ArgumentProperties(**kwargs)

    @property
    def _parser_argument(self):
        return getattr(self, '__parser_argument')

    @_parser_argument.setter
    def _parser_argument(self, parser_argument):
        setattr(self, '__parser_argument', parser_argument)
