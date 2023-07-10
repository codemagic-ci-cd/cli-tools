from __future__ import annotations

import json
import shlex
import sys
import traceback
from datetime import datetime
from datetime import timezone
from types import TracebackType
from typing import Type

from codemagic import __version__

from .base_auditor import BaseAuditor


class ExceptionAuditor(BaseAuditor):
    def __init__(
        self,
        exception_type: Type[BaseException],
        exception: BaseException,
        exception_traceback: TracebackType,
        audit_directory_name: str = "exceptions",
    ):
        super().__init__(audit_directory_name=audit_directory_name)
        self._exception_type = exception_type
        self._exception = exception
        self._traceback = exception_traceback

    def _get_audit_filename(self) -> str:
        if self._exception_type:
            exception_name = self._exception_type.__name__
        else:
            exception_name = "UnknownException"
        return f'error-{exception_name}-{datetime.now().strftime("%H-%M-%S")}.json'

    def _serialize_exception_arguments(self):
        try:
            # Check if error arguments can be JSON serialized
            _ = json.dumps(self._exception.args)
        except (ValueError, TypeError):
            # If args cannot be JSON serialized in their original form
            # cast them to strings first
            return [str(arg) for arg in self._exception.args]

        return self._exception.args

    def _serialize_audit_info(self):
        return {
            "command": shlex.join(sys.argv),
            "exception_arguments": self._serialize_exception_arguments(),
            "exception_type": self._exception_type.__name__,
            "stacktrace": "".join(traceback.format_tb(self._traceback)),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": __version__,
        }


def save_exception_audit(audit_directory_name: str = "exceptions"):
    exception_type, exception, exception_traceback = sys.exc_info()
    if exception_type is None or exception is None or exception_traceback is None:
        return

    auditor = ExceptionAuditor(
        exception_type,
        exception,
        exception_traceback,
        audit_directory_name=audit_directory_name,
    )
    auditor.save_audit()
