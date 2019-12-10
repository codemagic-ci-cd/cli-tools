import os
import pathlib
import subprocess
import tempfile
from typing import Any
from typing import Callable
from typing import Optional
from typing import Sequence
from typing import Tuple

from OpenSSL.crypto import X509
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKeyWithSerialization

from codemagic_cli_tools.cli.cli_types import ObfuscationPattern
from codemagic_cli_tools.models import Certificate
from codemagic_cli_tools.models import PrivateKey

CommandRunner = Callable[[Tuple[str, ...], Optional[Sequence[ObfuscationPattern]]], None]


class P12Exporter:

    def __init__(self, x509: X509, rsa_key: RSAPrivateKeyWithSerialization, container_password: str):
        self.x509 = x509
        self.rsa_key = rsa_key
        self.container_password = container_password
        self._temp_pem_certificate_path = self._save_to_disk('cert', Certificate.x509_to_pem(self.x509))
        self._temp_private_key_path = self._save_to_disk('key', PrivateKey.rsa_to_pem(self.rsa_key))

    @classmethod
    def _save_to_disk(cls, prefix: str, pem: str):
        with tempfile.NamedTemporaryFile(mode='w', prefix=f'{prefix}_', suffix='.pem', delete=False) as tf:
            tf.write(pem)
            return pathlib.Path(tf.name)

    def _cleanup(self):
        for path in (self._temp_pem_certificate_path, self._temp_private_key_path):
            if path and path.exists():
                os.remove(str(path))

    @staticmethod
    def default_command_runner(command_args: Sequence[str], obfuscate_patterns: Any = None):
        p = subprocess.Popen(command_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            if b'unable to load private key' in stderr:
                raise ValueError('Invalid private key')
            raise IOError('Failed to create PKCS12 container')

    @classmethod
    def _get_export_path(cls, export_path: Optional[pathlib.Path]) -> pathlib.Path:
        if export_path is not None:
            return export_path
        with tempfile.NamedTemporaryFile(prefix='certificate', suffix='.p12', delete=False) as tf:
            return pathlib.Path(tf.name)

    def _get_export_args(self, p12_path: pathlib.Path) -> Tuple[str, ...]:
        return (
            'openssl', 'pkcs12', '-export',
            '-out', str(p12_path.expanduser()),
            '-in', str(self._temp_pem_certificate_path),
            '-inkey', str(self._temp_private_key_path),
            '-passout', f'pass:{self.container_password}'
        )

    def export(self,
               export_path: Optional[pathlib.Path] = None,
               command_runner: Optional[CommandRunner] = None) -> pathlib.Path:
        p12_path = self._get_export_path(export_path)
        export_args = self._get_export_args(p12_path)
        obfuscate_patterns = [export_args[-1]]
        if command_runner is None:
            command_runner = P12Exporter.default_command_runner

        try:
            command_runner(export_args, obfuscate_patterns)
            return p12_path
        finally:
            self._cleanup()
