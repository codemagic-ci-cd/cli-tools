import pathlib
import shutil
from abc import ABCMeta
from abc import abstractmethod
from typing import Optional

from codemagic.shell_tools.shell_tool import ShellTool


class JavaJarTool(ShellTool, metaclass=ABCMeta):
    def __init__(self, java: Optional[pathlib.Path] = None):
        self._java = self._get_java_path(java)
        if not self._jar.exists():
            raise IOError(f"{self._jar} does not exist")

    @property
    @abstractmethod
    def _jar(self) -> pathlib.Path:
        raise NotImplementedError()

    @classmethod
    def _get_java_path(cls, java_path: Optional[pathlib.Path]) -> pathlib.Path:
        if java_path and java_path.exists():
            return java_path
        elif java := shutil.which("java"):
            return pathlib.Path(java)
        else:
            raise IOError("java is not in PATH")
