from __future__ import annotations

import pathlib
import plistlib
import shutil
import subprocess
from functools import lru_cache
from typing import Dict

from packaging.version import Version

from codemagic.mixins import RunningCliAppMixin


class Xcode(RunningCliAppMixin):
    DERIVED_DATA_PATH = pathlib.Path("~/Library/Developer/Xcode/DerivedData/").expanduser()

    def __init__(self, developer_dir: pathlib.Path):
        self.developer_dir = developer_dir

    def __repr__(self):
        return f"{self.__class__.__name__}({self.developer_dir!r})"

    @lru_cache(1)
    def _get_version_info(self) -> Dict[str, str]:
        version_plist = self.developer_dir.parent / "version.plist"
        with version_plist.open("rb") as fd:
            return plistlib.load(fd)

    @property
    def version(self) -> Version:
        version_info = self._get_version_info()
        return Version(version_info["CFBundleShortVersionString"])

    @property
    def build_version(self) -> str:
        version_info = self._get_version_info()
        return version_info["ProductBuildVersion"]

    @classmethod
    def get_selected(cls) -> Xcode:
        if not shutil.which("xcode-select"):
            raise IOError("xcode-select executable is not present on system")
        cmd_args = ("xcode-select", "--print-path")
        cli_app = cls.get_current_cli_app()
        try:
            if cli_app:
                process = cli_app.execute(cmd_args, show_output=False)
                process.raise_for_returncode()
                developer_dir = process.stdout.strip()
            else:
                developer_dir = subprocess.check_output(cmd_args).decode().strip()
        except subprocess.CalledProcessError:
            raise IOError("Failed to get default Xcode")
        return Xcode(pathlib.Path(developer_dir))
