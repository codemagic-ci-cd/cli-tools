import pathlib
import shutil
import subprocess
import tempfile
from functools import lru_cache
from typing import Any
from typing import Dict
from typing import Sequence
from typing import Union
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from codemagic.mixins import RunningCliAppMixin

from .abstract_package import AbstractPackage


class MacOsPackage(RunningCliAppMixin, AbstractPackage):
    def _validate_package(self):
        try:
            return bool(self.package_info)
        except (FileNotFoundError, IOError) as package_error:
            raise IOError(f'Not a valid macOS application package at {self.path}') from package_error

    @classmethod
    def _ensure_pkgutil(cls):
        if shutil.which('pkgutil') is None:
            raise IOError('pkgutil executable is not present on system')

    def _run_pkgutil_command(self, command: Sequence[Union[str, pathlib.Path]]):
        process = None
        cli_app = self.get_current_cli_app()
        try:
            if cli_app:
                process = cli_app.execute(command)
                process.raise_for_returncode()
            else:
                subprocess.check_output(command, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            raise IOError('Processing package failed', process)

    def _extract_file(self, filename_pattern: str) -> bytes:
        self._ensure_pkgutil()
        with tempfile.TemporaryDirectory() as td:
            expanded_package_path = pathlib.Path(td, 'pkg')
            extract_args = ('pkgutil', '--expand', self.path, expanded_package_path)
            self._run_pkgutil_command(extract_args)

            try:
                file_path = next(expanded_package_path.glob(filename_pattern))
            except StopIteration:
                raise FileNotFoundError(filename_pattern, self.path)
            return file_path.read_bytes()

    @lru_cache(1)
    def _get_package_info(self) -> Element:
        package_info_contents = self._extract_file('*.pkg/PackageInfo')
        return ElementTree.fromstring(package_info_contents)

    @lru_cache()
    def _get_package_info_node(self, node_name: str) -> Element:
        for child_element in self.package_info:
            if child_element.tag == node_name:
                return child_element
        raise ValueError(f'Element {node_name!r} not found from PackageInfo')

    @property
    def package_info(self) -> Element:
        return self._get_package_info()

    @property
    def _bundle(self) -> Element:
        return self._get_package_info_node('bundle')

    @property
    def _payload(self) -> Element:
        return self._get_package_info_node('payload')

    @property
    def bundle_identifier(self) -> str:
        return (
            self._bundle.attrib.get('id')
            or self.package_info.attrib.get('identifier')
            or 'N/A'
        )

    @property
    def install_size(self) -> str:
        size = self._payload.attrib.get('installKBytes')
        return f'{size}KB' if size else 'N/A'

    @property
    def version(self) -> str:
        return (
            self._bundle.attrib.get('CFBundleShortVersionString')
            or self.package_info.attrib.get('version')
            or self.version_code
        )

    @property
    def version_code(self) -> str:
        return (
            self._bundle.attrib.get('CFBundleVersion')
            or self.package_info.attrib.get('format-version')
            or ''
        )

    def get_summary(self) -> Dict[str, Any]:
        return {
            'bundle_identifier': self.bundle_identifier,
            'install_size': self.install_size,
            'version': self.version,
            'version_code': self.version_code,
        }
