from __future__ import annotations

import textwrap
from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Optional

from requests import Response

from .resource import DictSerializable


@dataclass
class ErrorMeta(DictSerializable):
    associatedErrors: Optional[Dict[str, List[Error]]] = None

    def __post_init__(self):
        if self.associatedErrors is None:
            return
        for scope in self.associatedErrors.keys():
            self.associatedErrors[scope] = [
                Error(**error) if isinstance(error, dict) else error
                for error in self.associatedErrors[scope]
            ]

    def __str__(self):
        lines = []
        for scope, errors in (self.associatedErrors or {}).items():
            lines.extend(f'Associated error: {e}' for e in errors)
        return '\n'.join(lines)


@dataclass
class Error(DictSerializable):
    _OMIT_IF_NONE_KEYS = ('meta', 'source', 'links')

    code: str
    status: str
    title: str
    detail: str
    id: Optional[str] = None
    source: Optional[Dict[str, str]] = None
    meta: Optional[ErrorMeta] = None
    links: Optional[Dict[str, str]] = None

    def __post_init__(self):
        if isinstance(self.meta, dict):
            self.meta = ErrorMeta(**self.meta)

    def __str__(self):
        s = f'{self.title} - {self.detail}'
        if self.meta:
            meta = textwrap.indent(str(self.meta), '\t')
            if meta:
                s += f'\n{meta}'
        return s


class ErrorResponse(DictSerializable):

    def __init__(self, api_response: Dict):
        self._raw = api_response
        self.errors = [Error(**error) for error in api_response['errors']]

    @classmethod
    def from_raw_response(cls, response: Response) -> ErrorResponse:
        error_response = ErrorResponse({'errors': []})
        error_response.errors.append(Error(
            code='NA',
            status=str(response.status_code),
            title='Request failed',
            detail=f'Request failed with status code {response.status_code}'))
        return error_response

    def __str__(self):
        return '\n'.join(map(str, self.errors))
