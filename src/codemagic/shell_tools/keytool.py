import pathlib
import subprocess
from tempfile import NamedTemporaryFile
from typing import AnyStr
from typing import Dict
from typing import Iterable
from typing import List
from typing import NoReturn
from typing import Optional
from typing import Sequence
from typing import Union

from codemagic.cli import CliProcess
from codemagic.models import Certificate
from codemagic.models import Keystore

from .abstract_shell_tool import AbstractShellTool


class Keytool(AbstractShellTool):
    """
    Minimal Python bindings for key and certificate management tool "keytool"
    """
    _executable_name = 'keytool'

    def _run_command(
        self,
        command: Sequence[str],
        command_env: Optional[Dict[str, str]] = None,
        suppress_output: bool = False,
    ) -> Union[subprocess.CompletedProcess, CliProcess]:
        cli_app = self.get_current_cli_app()

        if cli_app:
            cli_process = cli_app.execute(
                command,
                env=command_env,
                suppress_output=suppress_output,
            )
            cli_process.raise_for_returncode()
            return cli_process
        else:
            completed_process = subprocess.run(
                command,
                capture_output=True,
                env=command_env,
            )
            completed_process.check_returncode()
            return completed_process

    def generate_keystore(self, keystore: Keystore):
        command = (
            self.executable, '-genkey',
            '-alias', keystore.key_alias,
            '-keyalg', 'RSA',
            '-dname', keystore.certificate_attributes.get_distinguished_name(),
            '-validity', str(keystore.validity),
            '-keypass:env', 'KEY_PASSWORD',
            '-keystore', str(keystore.store_path),
            '-storepass:env', 'STORE_PASSWORD',
        )

        command_env = {
            'STORE_PASSWORD': keystore.store_password,
            'KEY_PASSWORD': keystore.key_password,
        }

        try:
            self._run_command(command, command_env=command_env)
        except subprocess.CalledProcessError as cpe:
            raise IOError('Failed to create keystore') from cpe

    def validate_keystore(
        self,
        keystore_path: pathlib.Path,
        keystore_password: str,
        key_alias: str,
    ) -> bool:
        command = (
            self.executable,
            '-rfc',
            '-list',
            '-alias', key_alias,
            '-keystore', str(keystore_path),
            '-storepass:env', 'STORE_PASSWORD',
        )

        try:
            self._run_command(
                command,
                command_env={'STORE_PASSWORD': keystore_password},
                suppress_output=True,
            )
        except subprocess.CalledProcessError as cpe:
            self._handle_keystore_list_error(cpe, key_alias=key_alias)
        return True

    def get_certificate(
        self,
        keystore_path: pathlib.Path,
        keystore_password: str,
        key_alias: str,
    ) -> Certificate:
        with NamedTemporaryFile(mode='wb') as tf:
            command = (
                self.executable,
                '-exportcert',
                '-storepass:env', 'STORE_PASSWORD',
                '-keystore', str(keystore_path),
                '-alias', key_alias,
                '-file', tf.name,
            )

            try:
                self._run_command(
                    command,
                    command_env={'STORE_PASSWORD': keystore_password},
                    suppress_output=True,
                )
            except subprocess.CalledProcessError as cpe:
                self._handle_keystore_list_error(cpe, key_alias=key_alias)
            else:
                asn1_certificate = pathlib.Path(tf.name).read_bytes()
                return Certificate.from_ans1(asn1_certificate)

    def get_certificates(
        self,
        keystore_path: pathlib.Path,
        keystore_password: str,
        key_alias: Optional[str] = None,
    ) -> List[Certificate]:
        alias_command_arguments = ('-alias', key_alias) if key_alias is not None else tuple()

        command = (
            self.executable,
            '-rfc',
            '-list',
            '-storepass:env', 'STORE_PASSWORD',
            '-keystore', str(keystore_path),
            *alias_command_arguments,
        )

        try:
            process = self._run_command(
                command,
                command_env={'STORE_PASSWORD': keystore_password},
                suppress_output=True,
            )
        except subprocess.CalledProcessError as cpe:
            self._handle_keystore_list_error(cpe, key_alias=key_alias)
        else:
            return list(self._iter_certificates(process.stdout))

    @classmethod
    def _handle_keystore_list_error(
        cls,
        error: subprocess.CalledProcessError,
        key_alias: Optional[str] = None,
    ) -> NoReturn:
        stdout = cls._str(error.stdout)
        if key_alias is not None and f'<{key_alias}> does not exist' in stdout:
            raise ValueError(f'Alias "{key_alias}" does not exist in keystore') from error
        elif 'keystore password was incorrect' in stdout:
            raise ValueError('Invalid keystore password') from error
        elif 'file does not exist' in stdout:
            raise ValueError('Keystore does not exist') from error
        elif 'Unrecognized keystore format' in stdout:
            raise ValueError('Unrecognized keystore format') from error
        else:
            raise ValueError(stdout.strip()) from error

    @classmethod
    def _iter_certificates(cls, certificates_rfc_output: AnyStr) -> Iterable[Certificate]:
        lines = cls._str(certificates_rfc_output).splitlines(keepends=True)
        pem = None
        for line in lines:
            if line.startswith('-----BEGIN '):
                pem = line
            elif pem is not None and line.startswith('-----END '):
                yield Certificate.from_pem(pem + line)
                pem = None
            elif pem is not None:
                pem += line
