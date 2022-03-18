import subprocess

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
            '-keypass:env', 'KEY_PASSWORD',
            '-keystore', str(keystore.store_path),
            '-storepass:env', 'STORE_PASSWORD',
        )

        command_env = {
            'STORE_PASSWORD': keystore.store_password,
            'KEY_PASSWORD': keystore.key_password,
        }

        cli_app = self.get_current_cli_app()
        try:
            if cli_app:
                cli_process = cli_app.execute(command, env=command_env)
                cli_process.raise_for_returncode()
            else:
                completed_process = subprocess.run(command, capture_output=True, env=command_env)
                completed_process.check_returncode()
        except subprocess.CalledProcessError as cpe:
            raise IOError('Failed to create keystore') from cpe

    def validate_keystore(self, keystore: Keystore):
        command = (
            self.executable, '-list',
            '-rfc',
            '-alias', keystore.key_alias,
            '-keystore', str(keystore.store_path),
            '-storepass:env', 'STORE_PASSWORD',
        )

        command_env = {'STORE_PASSWORD': keystore.store_password}

        cli_app = self.get_current_cli_app()
        try:
            if cli_app:
                cli_process = cli_app.execute(command, suppress_output=True, env=command_env)
                cli_process.raise_for_returncode()
            else:
                completed_process = subprocess.run(command, capture_output=True, env=command_env)
                completed_process.check_returncode()
        except subprocess.CalledProcessError as cpe:
            stdout = self._str(cpe.stdout)
            if f'<{keystore.key_alias}> does not exist' in stdout:
                raise ValueError(f'Alias "{keystore.key_alias}" does not exist in keystore') from cpe
            elif 'keystore password was incorrect' in stdout:
                raise ValueError('Invalid keystore password') from cpe
            elif 'file does not exist' in stdout:
                raise ValueError('Keystore does not exist') from cpe
            elif 'Unrecognized keystore format' in stdout:
                raise ValueError('Unrecognized keystore format') from cpe
            else:
                raise ValueError(stdout.strip()) from cpe
