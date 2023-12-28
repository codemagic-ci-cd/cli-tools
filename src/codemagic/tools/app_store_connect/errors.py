from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Optional

from codemagic import cli

if TYPE_CHECKING:
    from codemagic.apple.resources import ErrorResponse


class AppStoreConnectError(cli.CliAppException):
    def __init__(self, *args, api_error_response: Optional[ErrorResponse] = None, **kwargs):
        self.api_error = api_error_response
        super().__init__(*args, **kwargs)
