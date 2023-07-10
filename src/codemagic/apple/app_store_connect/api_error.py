import requests

from codemagic.apple.resources import ErrorResponse


class AppStoreConnectApiError(Exception):
    def __init__(self, response: requests.Response):
        self.response = response
        try:
            self.error_response = ErrorResponse(response.json())
        except ValueError:
            self.error_response = ErrorResponse.from_raw_response(response)

    @property
    def request(self) -> requests.PreparedRequest:
        return self.response.request

    @property
    def status_code(self) -> int:
        return self.response.status_code

    def __str__(self):
        return f"{self.request.method} {self.request.url} returned {self.response.status_code}: {self.error_response}"
