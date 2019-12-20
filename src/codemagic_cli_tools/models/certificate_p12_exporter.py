from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import tempfile
from typing import Optional
from typing import Sequence
from typing import TYPE_CHECKING
from typing import Tuple

from codemagic_cli_tools.mixins import StringConverterMixin

if TYPE_CHECKING:
    from .certificate import Certificate
    from .private_key import PrivateKey
    from codemagic_cli_tools.cli import CliApp


class P12Exporter(StringConverterMixin):

    def __init__(self, certificate: 'Certificate', private_key: 'PrivateKey', container_password: str):
        self.container_password = container_password
        self._temp_pem_certificate_path = self._save_to_disk('cert', certificate.as_pem())
        self._temp_private_key_path = self._save_to_disk('key', private_key.as_pem())

    @classmethod
    def _save_to_disk(cls, prefix: str, pem: str):
        with tempfile.NamedTemporaryFile(mode='w', prefix=f'{prefix}_', suffix='.pem', delete=False) as tf:
            tf.write(pem)
            return pathlib.Path(tf.name)

    def _cleanup(self):
        for path in (self._temp_pem_certificate_path, self._temp_private_key_path):
            if path and path.exists():
                os.remove(str(path))

    @classmethod
    def _get_export_path(cls, export_path: Optional[pathlib.Path]) -> pathlib.Path:
        if export_path is not None:
            return export_path
        with tempfile.NamedTemporaryFile(prefix='certificate', suffix='.p12', delete=False) as tf:
            return pathlib.Path(tf.name)

    @classmethod
    def _ensure_openssl(cls):
        if shutil.which('openssl') is None:
            raise IOError('OpenSSL executable not present on system')

    def _get_export_args(self, p12_path: pathlib.Path) -> Tuple[str, ...]:
        return (
            'openssl', 'pkcs12', '-export',
            '-out', str(p12_path.expanduser()),
            '-in', str(self._temp_pem_certificate_path),
            '-inkey', str(self._temp_private_key_path),
            '-passout', f'pass:{self.container_password}'
        )

    def _run_export_command(self, command: Sequence[str], cli_app: Optional['CliApp']):
        process = None
        try:
            if cli_app:
                process = cli_app.execute(command, [command[-1]])
                process.raise_for_returncode()
            else:
                subprocess.check_output(command, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as cpe:
            if 'unable to load private key' in self._str(cpe.stderr):
                error = 'Unable to export certificate: Invalid private key'
            else:
                error = 'Unable to export certificate: Failed to create PKCS12 container'
            raise IOError(error, process)

    def export(self,
               export_path: Optional[pathlib.Path] = None,
               *,
               cli_app: Optional['CliApp'] = None) -> pathlib.Path:
        self._ensure_openssl()
        p12_path = self._get_export_path(export_path)
        export_args = self._get_export_args(p12_path)
        try:
            self._run_export_command(export_args, cli_app)
        finally:
            self._cleanup()
        return p12_path
