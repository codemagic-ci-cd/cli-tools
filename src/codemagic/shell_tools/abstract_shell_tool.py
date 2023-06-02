import pathlib
import shutil
from abc import ABCMeta
from abc import abstractmethod

from codemagic.mixins import RunningCliAppMixin
from codemagic.mixins import StringConverterMixin


class AbstractShellTool(
    RunningCliAppMixin,
    StringConverterMixin,
    metaclass=ABCMeta,
):
    def __init__(self):
        self._ensure_executable()

    @property
    @abstractmethod
    def _executable_name(self) -> str:
        raise NotImplementedError()

    @property
    def executable(self) -> str:
        executable = shutil.which(self._executable_name)
        if executable is None:
            raise ValueError(f'{self._executable_name!r} executable is not present on the system')
        return pathlib.Path(executable).name

    def _ensure_executable(self):
        try:
            _ = self.executable
        except ValueError as ve:
            raise IOError(*ve.args) from ve
