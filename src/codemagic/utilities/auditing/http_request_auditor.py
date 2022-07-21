import re
import urllib.parse
from datetime import datetime
from typing import Dict
from typing import Optional

from requests import Response

from .base_auditor import BaseAuditor


class HttpRequestAuditor(BaseAuditor):
    def __init__(
        self,
        response: Response,
        audit_directory_name: str = 'http-requests',
    ):
        super().__init__(audit_directory_name=audit_directory_name)
        self.response = response
        self.request = response.request

    def _parse_request_url(self):
        return urllib.parse.urlparse(self.request.url)

    def _get_audit_filename(self) -> str:
        parsed_url = self._parse_request_url()
        sanitized_path = re.sub(r'[^\w_-]', '-', parsed_url.path)
        timestamp = datetime.now().strftime('%d-%m-%y-%H-%M-%S')
        return f'http-{self.request.method}-{self.response.status_code}-{sanitized_path}-{timestamp}.json'

    def _serialize_request_body(self) -> Optional[str]:
        if self.request.body is None:
            return None
        if isinstance(self.request.body, str):
            return self.request.body

        try:
            return self.request.body.decode()
        except ValueError:
            return '<binary_blob>'

    def _serialize_response_content(self) -> Optional[str]:
        if not self.response.content:
            return None

        try:
            return self.response.content.decode()
        except ValueError:
            return '<binary_blob>'

    def _serialize_request_headers(self) -> Dict[str, str]:
        serialized_headers = dict(self.request.headers)
        if 'Authorization' in self.request.headers:
            serialized_headers['Authorization'] = 'Bearer <token>'
        return serialized_headers

    def _serialize_audit_info(self):
        parsed_url = self._parse_request_url()
        return {
            'request': {
                'method': self.request.method,
                'url': self.request.url,
                'path': parsed_url.path,
                'headers': self._serialize_request_headers(),
                'body': self._serialize_request_body(),
                'query': urllib.parse.parse_qs(parsed_url.query),
            },
            'response': {
                'status_code': self.response.status_code,
                'headers': dict(self.response.headers),
                'content': self._serialize_response_content(),
                'elapsed': self.response.elapsed.total_seconds(),
            },
        }


def save_http_request_audit(response: Response, audit_directory_name: str = 'http-requests'):
    auditor = HttpRequestAuditor(response, audit_directory_name=audit_directory_name)
    auditor.save_audit()
