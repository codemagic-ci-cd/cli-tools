from __future__ import annotations

import abc
from typing import Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codemagic.cli import CliApp


class RunningCliAppMixin(metaclass=abc.ABCMeta):

    @classmethod
    def cli_app(cls) -> Optional[CliApp]:
        return cls.get_current_cli_app()

    @classmethod
    def get_current_cli_app(cls) -> Optional[CliApp]:
        from codemagic.cli import CliApp
        return CliApp.get_running_app()
