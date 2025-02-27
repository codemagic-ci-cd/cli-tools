from __future__ import annotations

import pathlib
import subprocess
import sys
from functools import cached_property
from typing import TYPE_CHECKING
from typing import Any
from typing import Dict
from typing import Optional

from cryptography import x509
from cryptography.x509 import load_der_x509_certificate

from codemagic.cli import CliApp
from codemagic.cli import Colors

from .abstract_package import AbstractPackage

if TYPE_CHECKING:
    from androguard.core.apk import APK

    from codemagic.models import Certificate


def _install_missing_androguard():
    commands = [
        [sys.executable, "-m", "ensurepip"],
        [sys.executable, "-m", "pip", "install", "androguard"],
    ]
    if cli_app := CliApp.get_running_app():
        cli_app.logger.info(Colors.WHITE("Installing missing tools to work with APK files..."))
        try:
            for command in commands:
                cli_process = cli_app.execute(command, show_output=False)
                cli_process.raise_for_returncode()
        except subprocess.CalledProcessError:
            cli_app.logger.error(Colors.RED("ERROR: Installing Androguard failed."))
            raise
    else:
        for command in commands:
            subprocess.run(command, check=True)


def _get_androguard_apk(apk_path: pathlib.Path, _install_androguard: bool = True) -> APK:
    try:
        from androguard.core.apk import APK
        from androguard.util import set_log
    except ImportError:
        if not _install_androguard:
            raise
        _install_missing_androguard()
        return _get_androguard_apk(apk_path, _install_androguard=False)

    # Silence androguard warnings
    set_log("ERROR")
    return APK(str(apk_path))


class ApkPackage(AbstractPackage):
    def _validate_package(self):
        try:
            _ = self._apk
        except ValueError as ve:
            # In case the file is not a valid Zip archive
            raise IOError(f"Not a valid APK at {self.path}") from ve

        if not self._apk.is_valid_APK():
            raise IOError(f"Not a valid APK at {self.path}")

    @cached_property
    def _apk(self) -> "APK":
        return _get_androguard_apk(self.path)

    @cached_property
    def certificate(self) -> Optional[Certificate]:
        from codemagic.models import Certificate

        certificate_name = self._apk.get_signature_name()
        if certificate_name is None:
            return None
        der_x509_certificate = self._apk.get_certificate_der(certificate_name)
        if not der_x509_certificate:
            return None
        certificate: x509.Certificate = load_der_x509_certificate(der_x509_certificate)
        if not certificate:
            return None
        return Certificate(certificate)

    def get_app_name(self) -> str:
        try:
            return self._apk.get_app_name()
        except ValueError as ve:
            if str(ve).startswith("ID is not a hex ID"):
                # This can happen if resolved application name starts with "@" symbol.
                # Androguard then treats it as a resource and tries to resolve its value
                # from Android resources, which of course fails.
                app_name = self._apk.get_attribute_value("application", "label") or ""
                if app_name.startswith("@"):
                    return app_name
            raise  # Unknown error, propagate further

    def get_package_name(self) -> str:
        return self._apk.get_package()

    def get_minimum_os_version(self) -> str:
        return self._apk.get_min_sdk_version()

    def is_debuggable(self) -> bool:
        return self._apk.get_attribute_value("application", "debuggable") == "true"

    def get_version_name(self):
        return str(self._apk.get_androidversion_name()) or ""

    def get_version_code(self) -> str:
        return str(self._apk.get_androidversion_code()) or ""

    def get_version(self) -> str:
        """
        https://developer.android.com/studio/publish/versioning
        """
        return self.get_version_name() or self.get_version_code()

    def get_summary(self) -> Dict[str, Any]:
        return {
            "app_name": self.get_app_name(),
            "package_name": self.get_package_name(),
            "min_os_version": self.get_minimum_os_version(),
            "certificate_issuer": self._format_name(self.certificate.issuer) if self.certificate else None,
            "certificate_subject": self._format_name(self.certificate.subject) if self.certificate else None,
            "debuggable": self.is_debuggable(),
            "version": self.get_version(),
            "version_code": self.get_version_code(),
        }
