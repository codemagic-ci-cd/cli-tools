import pathlib
import shutil
from abc import ABCMeta
from abc import abstractmethod
from typing import Optional

from codemagic.shell_tools.shell_tool import ShellTool


class JavaJarTool(ShellTool, metaclass=ABCMeta):
    def __init__(self, java: Optional[pathlib.Path] = None, jar: Optional[pathlib.Path] = None):
        self.__java = self._get_java_path(java)
        self.__jar = self._get_jar_path(jar)
        if not self.__jar.exists():
            raise IOError(f"{self.__jar} does not exist")

    @property
    def java(self) -> pathlib.Path:
        return self.__java

    @property
    def jar(self) -> pathlib.Path:
        return self.__jar

    @abstractmethod
    def _get_jar_path(self, jar_path: Optional[pathlib.Path]) -> pathlib.Path:
        raise NotImplementedError()

    @classmethod
    def _get_java_path(cls, java_path: Optional[pathlib.Path]) -> pathlib.Path:
        if java_path and java_path.exists():
            return java_path
        elif java := shutil.which("java"):
            return pathlib.Path(java)
        else:
            raise IOError("java is not in PATH")
