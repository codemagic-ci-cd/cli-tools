from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import tempfile
from typing import TYPE_CHECKING
from typing import Optional
from typing import Sequence
from typing import Union

from codemagic.mixins import RunningCliAppMixin
from codemagic.mixins import StringConverterMixin

if TYPE_CHECKING:
    from .certificate import Certificate
    from .private_key import PrivateKey


class P12Exporter(RunningCliAppMixin, StringConverterMixin):

    def __init__(self, certificate: Certificate, private_key: PrivateKey, container_password: str):
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

    def _run_openssl_command(self, command: Sequence[Union[str, pathlib.Path]]):
        process = None
        cli_app = self.get_current_cli_app()
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

    def _create_pkcs12_container(self, pkcs12: pathlib.Path, password: str):
        if not password:
            raise ValueError('Cannot export PKCS12 container without password')

        export_args = (
            'openssl', 'pkcs12', '-export',
            '-out', pkcs12.expanduser(),
            '-in', self._temp_pem_certificate_path,
            '-inkey', self._temp_private_key_path,
            '-passout', f'pass:{password}',
        )
        self._run_openssl_command(export_args)

    def _decrypt_pkcs12_container(self, pkcs12: pathlib.Path, password: str):
        if not password:
            raise ValueError('Cannot decrypt PKCS12 container without password')

        decrypted_pkcs12 = pkcs12.parent / f'{pkcs12.stem}_decrypted{pkcs12.suffix}'
        decrypt_args = (
            'openssl', 'pkcs12', '-nodes',
            '-passin', f'pass:{password}',
            '-in', pkcs12,
            '-out', decrypted_pkcs12,
        )
        self._run_openssl_command(decrypt_args)
        decrypted_pkcs12.rename(pkcs12)

    def export(self, export_path: Optional[pathlib.Path] = None) -> pathlib.Path:
        self._ensure_openssl()
        p12_path = self._get_export_path(export_path)
        password = self.container_password or 'temporary-password'
        try:
            self._create_pkcs12_container(p12_path, password)
            if not self.container_password:
                self._decrypt_pkcs12_container(p12_path, password)
        finally:
            self._cleanup()
        return p12_path
