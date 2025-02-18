from __future__ import annotations

import textwrap
from dataclasses import dataclass
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional

from requests import Response

from .resource import AppleDictSerializable


@dataclass
class ErrorMeta(AppleDictSerializable):
    associatedErrors: Optional[Dict[str, List[Error]]] = None

    def __post_init__(self):
        if self.associatedErrors is None:
            return
        for scope in self.associatedErrors.keys():
            self.associatedErrors[scope] = [
                Error(**error) if isinstance(error, dict) else error for error in self.associatedErrors[scope]
            ]

    def __str__(self):
        lines = []
        for scope, errors in (self.associatedErrors or {}).items():
            lines.extend(f"Associated error: {e}" for e in errors)
        return "\n".join(lines)


@dataclass
class Error(AppleDictSerializable):
    _OMIT_IF_NONE_KEYS = ("meta", "source", "links")

    code: str
    status: str
    title: str
    detail: Optional[str] = None
    id: Optional[str] = None
    source: Optional[Dict[str, str]] = None
    meta: Optional[ErrorMeta] = None
    links: Optional[Dict[str, str]] = None

    @property
    def associated_errors(self) -> Dict[str, List[Error]]:
        if not self.meta or not self.meta.associatedErrors:
            return {}
        return self.meta.associatedErrors

    @property
    def source_pointer(self) -> Optional[str]:
        try:
            return self.source["pointer"] if self.source else None
        except KeyError:
            return None

    def __post_init__(self):
        if isinstance(self.meta, dict):
            self.meta = ErrorMeta(**self.meta)

    def __str__(self):
        if self.detail is None:
            s = self.title
        else:
            s = f"{self.title} - {self.detail}"

        if self.meta:
            meta = textwrap.indent(str(self.meta), "\t")
            if meta:
                s += f"\n{meta}"
        return s


class ErrorResponse(AppleDictSerializable):
    def __init__(self, api_response: Dict):
        self._raw = api_response
        self.errors = [Error(**error) for error in api_response["errors"]]

    @classmethod
    def from_raw_response(cls, response: Response) -> ErrorResponse:
        error_response = ErrorResponse({"errors": []})
        error_response.errors.append(
            Error(
                code="NA",
                status=str(response.status_code),
                title="Request failed",
                detail=f"Request failed with status code {response.status_code}",
            ),
        )
        return error_response

    def iter_associated_errors(self) -> Iterable[Error]:
        for error in self.errors:
            for errors in error.associated_errors.values():
                yield from errors

    def __str__(self):
        return "\n".join(map(str, self.errors))
