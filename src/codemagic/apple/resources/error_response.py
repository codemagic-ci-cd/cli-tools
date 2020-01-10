from __future__ import annotations

from dataclasses import dataclass
from typing import Dict
from typing import Optional

from requests import Response

from .resource import DictSerializable


@dataclass
class Error(DictSerializable):
    code: str
    status: str
    title: str
    detail: str
    id: Optional[str] = None
    source: Optional[Dict[str, str]] = None


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
        return '\n'.join(f'{error.title} - {error.detail}' for error in self.errors)
