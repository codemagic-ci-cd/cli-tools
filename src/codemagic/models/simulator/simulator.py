from __future__ import annotations

import pathlib
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict
from typing import Union


@dataclass
class Simulator:
    udid: str
    is_available: bool
    state: str
    name: str
    data_path: pathlib.Path
    log_path: pathlib.Path

    def __post_init__(self):
        if isinstance(self.data_path, str):
            self.data_path = pathlib.Path(self.data_path)
        if isinstance(self.log_path, str):
            self.log_path = pathlib.Path(self.log_path)

    @classmethod
    def create(cls, **kwargs) -> Simulator:
        @lru_cache()
        def camel_to_snake(s: str) -> str:
            return re.sub(r'([A-Z])', lambda m: f'_{m.group(1).lower()}', s)

        return Simulator(**{
            camel_to_snake(name): value for name, value in kwargs.items()
            if camel_to_snake(name) in cls.__dataclass_fields__
        })

    def dict(self) -> Dict[str, Union[str, bool]]:
        return {**self.__dict__, 'data_path': str(self.data_path), 'log_path': str(self.log_path)}

    def __repr__(self):
        return f'<Simulator: {self.name!r}>'
