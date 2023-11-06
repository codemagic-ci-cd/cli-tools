from __future__ import annotations

import pathlib
import plistlib
import shutil
import subprocess
import tempfile
from typing import Any
from typing import AnyStr
from typing import Dict
from typing import List
from typing import Tuple

from packaging.version import Version

from codemagic.mixins import RunningCliAppMixin
from codemagic.mixins import StringConverterMixin
from codemagic.utilities import log

from .application_package import Ipa


class CodeSignEntitlements(RunningCliAppMixin, StringConverterMixin):
    def __init__(self, entitlement_data: Dict[str, Any]):
        self.plist: Dict[str, Any] = entitlement_data
        self.logger = log.get_logger(self.__class__)

    @classmethod
    def _ensure_codesign(cls):
        if shutil.which("codesign") is None:
            raise IOError('Missing executable "codesign"')

    @classmethod
    def from_plist(cls, plist: AnyStr) -> CodeSignEntitlements:
        parsed_plist = plistlib.loads(cls._bytes(plist))
        return CodeSignEntitlements(parsed_plist)

    @classmethod
    def _get_codesign_command(cls, app_path: pathlib.Path) -> Tuple[str, ...]:
        from codemagic.models import Xcode

        if Xcode.get_selected().version < Version("13.3"):
            # The "--entitlements" option of codesign takes "path" parameter to specify where the
            # entitlements should be displayed. In order to send the output to stdout instead
            # of file, "-" needs to be specified. Until Xcode 13.2 it had the following
            # behaviour according to manpage:
            # > By default, the binary "blob" header is returned intact;
            # > prefix the path with a colon ":" to automatically strip it off.
            # Hence entitlements path needs to be given as ":-".
            command: Tuple[str, ...] = ("codesign", "--display", "--entitlements", ":-", str(app_path))
        else:
            # Starting from Xcode 13.3 codesign command line API changed a little.
            # By default the displayed information is not in plist/xml format any more:
            # > The format is designed to be moderately easy to parse by simple
            # > scripts while still making sense to human eyes.
            # Hence the need for additional "--xml" option. Additionally
            # specifying ':' in the path was deprecated and when xml formatting is requested,
            # then binary blob header is automatically removed.
            command = ("codesign", "--display", "--entitlements", "-", "--xml", str(app_path))
        return command

    @classmethod
    def from_app(cls, app_path: pathlib.Path) -> CodeSignEntitlements:
        cls._ensure_codesign()
        cmd = cls._get_codesign_command(app_path)
        cli_app = cls.get_current_cli_app()
        try:
            if cli_app:
                process = cli_app.execute(cmd, show_output=False)
                process.raise_for_returncode()
                output = cls._bytes(process.stdout)
            else:
                output = subprocess.check_output(cmd, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as cpe:
            raise IOError(f"Failed to obtain entitlements from {app_path}, {cls._str(cpe.stderr)}")

        # With Xcode 13.3+ codesign adds a 0 byte to the end of the XML formatted plist
        plist = cls._bytes(output).rstrip(b"\x00")

        return cls.from_plist(plist)

    @classmethod
    def from_ipa(cls, ipa_path: pathlib.Path) -> CodeSignEntitlements:
        with tempfile.TemporaryDirectory() as td:
            try:
                app_path = Ipa(ipa_path).extract_app(pathlib.Path(td))
            except IOError:
                raise IOError(f"Failed to obtain entitlements from {ipa_path}, .app not found")
            return cls.from_app(app_path)

    @classmethod
    def from_xcarchive(cls, xcarchive_path: pathlib.Path) -> CodeSignEntitlements:
        app_path = next((xcarchive_path.glob("Products/Applications/*.app")), None)
        if not app_path:
            raise IOError(f"Failed to obtain entitlements from {xcarchive_path}, .app not found")
        return cls.from_app(app_path)

    def get_icloud_container_environments(self) -> List[str]:
        environment = self.plist.get("com.apple.developer.icloud-container-environment")
        if environment is None:
            return []
        elif isinstance(environment, str):
            return [environment]
        elif isinstance(environment, list):
            return environment
        raise ValueError(f"Unknown type for environment: {type(environment)}")

    def get_icloud_services(self) -> List[str]:
        return self.plist.get("com.apple.developer.icloud-services", [])
