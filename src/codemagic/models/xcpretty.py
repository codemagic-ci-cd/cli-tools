import shlex
import shutil
import subprocess
import sys
from typing import IO
from typing import AnyStr
from typing import Optional
from typing import Union

from codemagic.mixins import StringConverterMixin

_IO = Union[int, IO]


class Xcpretty(StringConverterMixin):

    def __init__(self, custom_options: str = '', stdout: _IO = sys.stdout, stderr: _IO = sys.stderr):
        self._ensure_xcpretty()
        self._command = ['xcpretty'] + shlex.split(custom_options)
        self._process: Optional[subprocess.Popen] = None
        self._stdout: _IO = stdout
        self._stderr: _IO = stderr

    @classmethod
    def _ensure_xcpretty(cls):
        if shutil.which('xcpretty') is None:
            raise IOError('xcpretty executable not present on the system')

    def format(self, chunk: AnyStr):
        if not chunk:
            return

        if self._process is None:
            self._process = subprocess.Popen(
                self._command,
                stdin=subprocess.PIPE,
                stdout=self._stdout,
                stderr=self._stderr,
            )

        if self._process.stdin:
            self._process.stdin.write(self._bytes(chunk))

    def flush(self):
        if self._process is None:
            return

        try:
            self._process.communicate(b'', timeout=5)
        except subprocess.TimeoutExpired:
            pass
        finally:
            self._process.terminate()
            self._process = None
