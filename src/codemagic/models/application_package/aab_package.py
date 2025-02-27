from __future__ import annotations

import pathlib
import subprocess
import zipfile
from functools import cached_property
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional

from cryptography import x509
from cryptography.hazmat.primitives.serialization.pkcs7 import load_der_pkcs7_certificates

from .abstract_package import AbstractPackage
from .android import AndroidManifest
from .android import AppBundleResources
from .android import Strings

if TYPE_CHECKING:
    from codemagic.models import Certificate
    from codemagic.shell_tools.bundletool import Bundletool


class AabPackage(AbstractPackage):
    def _validate_package(self):
        try:
            self._bundletool.validate(
                bundle=self.path,
                show_output=False,
            )
        except subprocess.CalledProcessError as cpe:
            raise IOError(f"Not a valid Android App Bundle at {self.path}") from cpe

    def _extract_file(self, filename_filter: Callable[[str], bool]) -> bytes:
        with zipfile.ZipFile(self.path) as zf:
            try:
                found_file_name = next(filter(filename_filter, zf.namelist()))
            except StopIteration:
                raise FileNotFoundError(f"File not found for {filename_filter.__name__}", self.path)
            with zf.open(found_file_name, "r") as fd:
                return fd.read()

    @cached_property
    def _bundletool(self) -> Bundletool:
        from codemagic.shell_tools.bundletool import Bundletool

        return Bundletool()

    @cached_property
    def _manifest(self) -> AndroidManifest:
        manifest_xml = self._bundletool.dump(
            "manifest",
            self.path,
            show_output=False,
        )
        return AndroidManifest(manifest_xml)

    @cached_property
    def _resources(self) -> AppBundleResources:
        # Disable bundletool error checks as even valid aabs might have some resource
        # declarations missing, which will cause the overall command to exit with error code 1
        # while all valid resources are printed out to STDOUT stream.
        try:
            resources_dump = self._bundletool.dump(
                "resources",
                self.path,
                values=True,
                show_output=False,
            )
        except subprocess.CalledProcessError as cpe:
            resources_dump = self._str(cpe.stdout)

        if not resources_dump.strip():
            raise IOError("Failed to dump resources from aab")
        return AppBundleResources(resources_dump)

    @cached_property
    def _strings(self) -> Strings:
        strings_xml_path = pathlib.Path("base/root/values/strings.xml")

        def strings_xml_filter(path_name: str) -> bool:
            return pathlib.Path(path_name) == strings_xml_path

        strings_xml_filter.__name__ = f"strings {strings_xml_path!r} filter"

        try:
            xml = self._extract_file(strings_xml_filter)
        except FileNotFoundError:
            xml = b"""<resources></resources>"""

        return Strings(xml)

    def _get_signature(self) -> Optional[pathlib.Path]:
        with zipfile.ZipFile(self.path) as zf:
            namelist = zf.namelist()
            for path_in_zip in map(pathlib.Path, namelist):
                # Signatures are stored in ./META-INF/<signature-name>.(RSA|EC|DSA)
                # Full signature also has ./META-INF/<signature-name>.SF next to it
                is_signature = path_in_zip.parent.name == "META-INF" and path_in_zip.suffix in (".RSA", ".EC", ".DSA")
                sf_file_path = path_in_zip.parent / f"{path_in_zip.stem}.SF"
                if is_signature and str(sf_file_path) in namelist:
                    return path_in_zip
        return None

    @cached_property
    def certificate(self) -> Optional[Certificate]:
        from codemagic.models import Certificate

        certificate_path = self._get_signature()
        if not certificate_path:
            return None

        def certificate_filter(path_name: str) -> bool:
            return pathlib.Path(path_name) == certificate_path

        certificate_filter.__name__ = f"certificate {certificate_path!r} filter"

        cert_pkcs7_message = self._extract_file(certificate_filter)
        certificates: List[x509.Certificate] = load_der_pkcs7_certificates(cert_pkcs7_message)
        if not certificates:
            return None
        return Certificate(certificates[0])

    def get_app_name(self) -> str:
        label = self._manifest.app_label
        if label.startswith("@") and (resource_value := self._resources.get_resource(label[1:])):
            label = resource_value
        if label.startswith("@string/"):
            string_reference = label[8:]
            return self._strings.get_value(string_reference) or string_reference
        return label

    def get_version(self) -> str:
        return self._manifest.version_name or self._manifest.version_code

    def get_version_code(self):
        return self._manifest.version_code

    def get_version_name(self):
        return self._manifest.version_name

    def get_minimum_os_version(self) -> str:
        return self._manifest.min_sdk_version

    def get_package_name(self) -> str:
        return self._manifest.package_name

    def is_debuggable(self) -> bool:
        return self._manifest.debuggable == "true"

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
