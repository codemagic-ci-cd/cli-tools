from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List
from typing import Optional


@dataclass
class ResultBase:
    @classmethod
    def _convert_field_name(cls, name: str) -> str:
        name = name.replace('-', '_')
        name = re.sub(r'^NSLocalized', '', name)
        name = f'{name[0].lower()}{name[1:]}'
        return re.sub(r'([A-Z])', lambda m: f'_{m.group(1).lower()}', name)

    @classmethod
    def create(cls, **kwargs):
        return cls(**{
            cls._convert_field_name(name): value
            for name, value in kwargs.items()
        })


@dataclass
class UserInfo(ResultBase):
    failure_reason: str
    recovery_suggestion: str
    description: str


@dataclass
class ProductError(ResultBase):
    message: str
    user_info: UserInfo
    code: int

    def __post_init__(self):
        if self.user_info and not isinstance(self.user_info, UserInfo):
            self.user_info = UserInfo.create(**self.user_info)


@dataclass
class AltoolResult(ResultBase):
    tool_version: str
    tool_path: str
    os_version: str
    success_message: Optional[str] = None
    product_errors: Optional[List[ProductError]] = None

    def __post_init__(self):
        if self.product_errors and not isinstance(self.product_errors[0], ProductError):
            self.product_errors = [ProductError.create(**pe) for pe in self.product_errors]
