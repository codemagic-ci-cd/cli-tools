import shlex
import shutil
import subprocess
import sys
from typing import AnyStr
from typing import IO
from typing import Union

from codemagic.mixins import StringConverterMixin

_IO = Union[int, IO]


class Xcpretty(StringConverterMixin):

    def __init__(self, custom_options: str = ''):
        self._ensure_xcpretty()
        self._command = ['xcpretty'] + shlex.split(custom_options)

    @classmethod
    def _ensure_xcpretty(cls):
        if shutil.which('xcpretty') is None:
            raise IOError('xcpretty executable not present on the system')

    def format(self, chunk: AnyStr, stdout: _IO = sys.stdout, stderr: _IO = sys.stderr, timeout: int = 2):
        if not chunk:
            return
        process = subprocess.Popen(
            self._command,
            stdin=subprocess.PIPE,
            stdout=stdout,
            stderr=stderr,
        )
        try:
            process.communicate(input=self._bytes(chunk), timeout=timeout)
        except subprocess.TimeoutExpired:
            pass
        except KeyboardInterrupt:
            process.terminate()
            raise
