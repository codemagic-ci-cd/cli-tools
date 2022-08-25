import re
import urllib.parse
from datetime import datetime
from typing import Dict
from typing import Optional

from requests import Response

from codemagic import __version__

from .base_auditor import BaseAuditor


class HttpRequestAuditor(BaseAuditor):
    def __init__(
        self,
        response: Response,
        audit_directory_name: str = 'http-requests',
    ):
        super().__init__(audit_directory_name=audit_directory_name)
        self._response = response

    @property
    def _request(self):
        return self._response.request

    def _parse_request_url(self):
        return urllib.parse.urlparse(self._request.url)

    def _get_audit_filename(self) -> str:
        parsed_url = self._parse_request_url()
        sanitized_path = re.sub(r'[^\w_-]', '-', parsed_url.path)
        timestamp = datetime.now().strftime('%H-%M-%S')
        return f'http-{self._request.method}-{self._response.status_code}-{sanitized_path}-{timestamp}.json'

    def _serialize_request_body(self) -> Optional[str]:
        if self._request.body is None:
            return None
        if isinstance(self._request.body, str):
            return self._request.body

        try:
            return self._request.body.decode()
        except ValueError:
            return '<binary_blob>'

    def _serialize_response_content(self) -> Optional[str]:
        if not self._response.content:
            return None

        try:
            return self._response.content.decode()
        except ValueError:
            return '<binary_blob>'

    def _serialize_request_headers(self) -> Dict[str, str]:
        serialized_headers = dict(self._request.headers)
        if 'Authorization' in self._request.headers:
            serialized_headers['Authorization'] = 'Bearer <token>'
        return serialized_headers

    def _serialize_audit_info(self):
        parsed_url = self._parse_request_url()
        return {
            'request': {
                'method': self._request.method,
                'url': self._request.url,
                'path': parsed_url.path,
                'headers': self._serialize_request_headers(),
                'body': self._serialize_request_body(),
                'query': urllib.parse.parse_qs(parsed_url.query),
            },
            'response': {
                'status_code': self._response.status_code,
                'headers': dict(self._response.headers),
                'content': self._serialize_response_content(),
                'elapsed': self._response.elapsed.total_seconds(),
            },
            'timestamp': datetime.utcnow().isoformat(),
            'version': __version__,
        }


def save_http_request_audit(response: Response, audit_directory_name: str = 'http-requests'):
    auditor = HttpRequestAuditor(response, audit_directory_name=audit_directory_name)
    auditor.save_audit()
