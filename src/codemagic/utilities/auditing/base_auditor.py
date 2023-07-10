import json
import os
import pathlib
import tempfile
from abc import ABC
from abc import abstractmethod
from datetime import datetime

from codemagic.utilities import log


class BaseAuditor(ABC):
    def __init__(self, audit_directory_name: str):
        self._audit_directory_name = audit_directory_name

    def _get_audit_dir(self) -> pathlib.Path:
        requests_audit_dir = pathlib.Path(
            tempfile.gettempdir(),
            "codemagic-cli-tools",
            self._audit_directory_name,
            datetime.now().strftime("%Y-%m-%d"),
        )
        requests_audit_dir.mkdir(parents=True, exist_ok=True)
        return requests_audit_dir

    @abstractmethod
    def _get_audit_filename(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def _serialize_audit_info(self):
        raise NotImplementedError()

    def _save_audit(self):
        audit_path = self._get_audit_dir() / self._get_audit_filename()
        with audit_path.open("w") as fd:
            json.dump(self._serialize_audit_info(), fd, indent=4)

    def save_audit(self):
        if os.environ.get("PYTEST_RUN_CONFIG", False):
            return  # Do not save audit info when running tests

        try:
            self._save_audit()
        except Exception:  # noqa
            file_logger = log.get_file_logger(self.__class__)
            file_logger.exception("Failed to save audit")
