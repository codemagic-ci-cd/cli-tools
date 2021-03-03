import logging
from typing import Any

__version__: str

class NullHandler(logging.Handler):
    def emit(self, record: Any) -> None: ...
