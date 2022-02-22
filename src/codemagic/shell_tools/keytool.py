import subprocess
from typing import Optional
from typing import Sequence

from codemagic.models import Keystore

from .abstract_shell_tool import AbstractShellTool


class Keytool(AbstractShellTool):
    """
    Minimal Python bindings for key and certificate management tool "keytool"
    """
    _executable_name = 'keytool'

    def generate_keystore(self, keystore: Keystore):
        command = (
            self.executable, '-genkey',
            '-alias', keystore.key_alias,
            '-keyalg', 'RSA',
            '-dname', keystore.certificate_attributes.get_distinguished_name(),
            '-validity', str(keystore.validity),
            '-keypass', keystore.key_password,
            '-keystore', str(keystore.path),
            '-storepass', keystore.store_password,
        )
        self._run_command(
            command,
            obfuscate_patterns=(keystore.store_password, keystore.key_password),
        )

    def _run_command(
            self,
            command: Sequence[str],
            obfuscate_patterns: Optional[Sequence[str]] = None,
    ):
        cli_app = self.get_current_cli_app()
        if cli_app:
            cli_process = cli_app.execute(command, obfuscate_patterns)
            cli_process.raise_for_returncode()
        else:
            _completed_process = subprocess.run(command, capture_output=True)
            _completed_process
        # TODO: return some common object
