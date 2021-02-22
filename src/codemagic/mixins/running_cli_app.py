from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Optional

if TYPE_CHECKING:
    from codemagic.cli import CliApp


class RunningCliAppMixin:

    @classmethod
    def get_current_cli_app(cls) -> Optional[CliApp]:
        from codemagic.cli import CliApp
        return CliApp.get_running_app()
