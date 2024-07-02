from __future__ import annotations

import contextlib
import pathlib
import re
import shutil
import subprocess
import tempfile
from typing import TYPE_CHECKING
from typing import AnyStr
from typing import Generator
from typing import Optional
from typing import Sequence
from typing import Union

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives._serialization import PrivateFormat
from cryptography.hazmat.primitives.serialization import pkcs12
from packaging.version import Version

from codemagic.mixins import RunningCliAppMixin
from codemagic.mixins import StringConverterMixin

if TYPE_CHECKING:
    from typing_extensions import Literal

    from .certificate import Certificate
    from .private_key import PrivateKey


class _OpenSsl:
    def __init__(self):
        self._executable = shutil.which("openssl")

    def ensure_installed(self):
        if self._executable is None:
            raise IOError("OpenSSL executable is not present on system")

    def get_version(self) -> Optional[Version]:
        if not self._executable:
            return None

        try:
            version_output = subprocess.check_output([self._executable, "version"])
        except subprocess.CalledProcessError:
            version_output = b""

        version_match = re.search(r"\d+\.\d+\.\d+", version_output.decode(errors="ignore"))
        if not version_match:
            return None

        return Version(version_match.group())

    @property
    def no_encryption_flag(self) -> Literal["-nodes", "-noenc"]:
        # Starting from OpenSSL version 3.0.0 `-nodes` is deprecated for disabling encryption
        # when invoking `openssl pkcs12`. It is replaced with `-noenc`.
        # See https://www.openssl.org/docs/man3.0/man1/openssl-pkcs12.html

        openssl_version = self.get_version()
        if openssl_version and openssl_version < Version("3.0.0"):
            # Use legacy flag only if we are sure that the version is earlier than 3.0.0
            return "-nodes"
        return "-noenc"


class P12Exporter(RunningCliAppMixin, StringConverterMixin):
    def __init__(
        self,
        certificate: Certificate,
        private_key: PrivateKey,
        container_password: Optional[str],
    ):
        self._password = container_password
        self._certificate = certificate
        self._private_key = private_key
        self._openssl = _OpenSsl()

    @contextlib.contextmanager
    def _temp_container(self) -> Generator[pathlib.Path, None, None]:
        with tempfile.NamedTemporaryFile(prefix="certificate_", suffix=".p12") as tf:
            yield pathlib.Path(tf.name)

    @classmethod
    def _get_export_path(cls, export_path: Optional[pathlib.Path]) -> pathlib.Path:
        if export_path is not None:
            return export_path
        with tempfile.NamedTemporaryFile(prefix="certificate", suffix=".p12", delete=False) as tf:
            return pathlib.Path(tf.name)

    def _run_openssl_command(self, command: Sequence[Union[str, pathlib.Path]]):
        process = None
        cli_app = self.get_current_cli_app()
        try:
            if cli_app:
                obfuscate_patterns = [arg for arg in command if str(arg).startswith("pass:")]
                process = cli_app.execute(command, obfuscate_patterns)
                process.raise_for_returncode()
            else:
                subprocess.check_output(command, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as cpe:
            if "unable to load private key" in self._str(cpe.stderr):
                error = "Unable to export certificate: Invalid private key"
            else:
                error = "Unable to export certificate: Failed to create PKCS12 container"
            raise IOError(error, process)

    def create_encrypted_pkcs12_container(self, password: str) -> bytes:
        # With OpenSSL 3.0.0+ the defaults for encryption when serializing PKCS12
        # have changed and some versions of Windows and macOS will not be able to
        # read the new format. Maximum compatibility can be achieved by using SHA1
        # for MAC algorithm and PBESv1SHA1And3KeyTripleDESCBC for encryption algorithm.

        if not password:
            raise ValueError("Cannot create encrypted PKCS12 container without password")

        encryption = (
            PrivateFormat.PKCS12.encryption_builder()
            .kdf_rounds(50000)
            .key_cert_algorithm(pkcs12.PBES.PBESv1SHA1And3KeyTripleDESCBC)
            .hmac_hash(hashes.SHA1())
            .build(self._bytes(password))
        )

        return pkcs12.serialize_key_and_certificates(
            None,
            self._private_key.cryptography_private_key,
            self._certificate.certificate,
            None,
            encryption,
        )

    def create_decrypted_pkcs12_container(self) -> bytes:
        # Create an encrypted container with temporary password first as macOS keychain
        # is not capable of handling non-encrypted PKCS#12 containers created by cryptography
        # as those use SHA256 for HMAC hash function.
        encrypted_pkcs12_container = self.create_encrypted_pkcs12_container("temporary-password")

        # Strip temporary password from the encrypted container to decrypt it
        return self._decrypt_pkcs12_container(encrypted_pkcs12_container, "temporary-password")

    def _decrypt_pkcs12_container(self, pkcs12_container: bytes, password: AnyStr) -> bytes:
        if not password:
            raise ValueError("Cannot decrypt PKCS12 container without password")

        with self._temp_container() as encrypted, self._temp_container() as decrypted:
            encrypted.write_bytes(pkcs12_container)
            decrypt_args = (
                *("openssl", "pkcs12", self._openssl.no_encryption_flag),
                *("-passin", f"pass:{self._str(password)}"),
                *("-in", encrypted),  # type: ignore
                *("-out", decrypted),  # type: ignore
            )
            self._run_openssl_command(decrypt_args)
            decrypted_container = decrypted.read_bytes()

        # Decrypted container is an ASCII text file that contains the PEM encoded
        # certificate and key along with their bag attributes, which are optional.
        # Remove subject line from bag attributes, which is not required but can
        # contain unicode characters that are not supported by macOS keychain.
        lines = decrypted_container.splitlines(keepends=True)
        return b"".join(line for line in lines if not line.startswith(b"subject="))

    def export(self, export_path: Optional[pathlib.Path] = None) -> pathlib.Path:
        self._openssl.ensure_installed()

        if self._password:
            pkcs12_container = self.create_encrypted_pkcs12_container(self._password)
        else:
            pkcs12_container = self.create_decrypted_pkcs12_container()

        p12_path = self._get_export_path(export_path)
        p12_path.write_bytes(pkcs12_container)
        return p12_path
