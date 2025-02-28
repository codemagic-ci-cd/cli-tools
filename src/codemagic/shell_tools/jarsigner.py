import pathlib
import shutil

from .shell_tool import ShellTool


class Jarsigner(ShellTool):
    """
    Minimal Python bindings for "jarsigner"
    """

    def __init__(self):
        self._executable = shutil.which("jarsigner")
        if not self._executable:
            raise IOError('"jarsigner" executable is not present on the system')
        super().__init__()

    def sign(
        self,
        file_to_sign: pathlib.Path,
        *,
        keystore: pathlib.Path,
        keystore_password: str,
        key_alias: str,
        key_password: str,
        verbose: bool = True,
        show_output: bool = False,
    ):
        self._run_command(
            (
                self._executable,
                *(["-verbose"] if verbose else []),
                *("-sigalg", "SHA1withRSA"),
                *("-digestalg", "SHA1"),
                *("-keystore", keystore),
                *("-storepass", keystore_password),
                *("-keypass", key_password),
                file_to_sign,
                key_alias,
            ),
            obfuscate_patterns=(keystore_password, key_password),
            show_output=show_output,
        )

    def verify(
        self,
        file_to_verify: pathlib.Path,
        *,
        verbose: bool = True,
        show_output: bool = False,
    ) -> str:
        completed_process = self._run_command(
            (
                self._executable,
                *(["-verbose"] if verbose else []),
                "-verify",
                file_to_verify,
            ),
            show_output=show_output,
        )
        return self._get_stdout(completed_process)
