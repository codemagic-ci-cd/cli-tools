from __future__ import annotations

import pathlib
import plistlib
import shutil
import subprocess
import tempfile
import zipfile
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import TYPE_CHECKING

from codemagic.mixins import StringConverterMixin
from codemagic.utilities import log

if TYPE_CHECKING:
    from codemagic.cli import CliApp


class CodeSignEntitlements(StringConverterMixin):

    def __init__(self, entitlement_data: Dict[str, Any]):
        self.plist: Dict[str, Any] = entitlement_data
        self.logger = log.get_logger(self.__class__)

    @classmethod
    def _ensure_codesign(cls):
        if shutil.which('codesign') is None:
            raise IOError('Missing executable "codesign"')

    @classmethod
    def from_app(cls, app_path: pathlib.Path, cli_app: Optional['CliApp'] = None) -> CodeSignEntitlements:
        cls._ensure_codesign()
        cmd = ('codesign', '-d', '--entitlements', ':-', str(app_path))
        try:
            if cli_app:
                process = cli_app.execute(cmd, show_output=False)
                process.raise_for_returncode()
                output = cls._bytes(process.stdout)
            else:
                output = subprocess.check_output(cmd, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as cpe:
            raise IOError(f'Failed to obtain entitlements from {app_path}, {cls._str(cpe.stderr)}')

        return CodeSignEntitlements(plistlib.loads(output))

    @classmethod
    def from_ipa(cls, ipa_path: pathlib.Path, cli_app: Optional['CliApp'] = None) -> CodeSignEntitlements:
        with zipfile.ZipFile(ipa_path) as zf, tempfile.TemporaryDirectory() as td:
            for zi in zf.filelist:
                path = pathlib.Path(zi.filename)
                try:
                    p1, p2, *_rest = path.parts
                except ValueError:
                    continue
                if p1 == 'Payload' and p2.endswith('.app'):
                    zf.extract(zi, path=td)

            app_path = next((pathlib.Path(td).glob('Payload/*.app')), None)
            if not app_path:
                raise IOError(f'Failed to obtain entitlements from {ipa_path}, .app not found')
            return cls.from_app(app_path, cli_app=cli_app)

    @classmethod
    def from_xcarchive(cls, xcarchive_path: pathlib.Path, cli_app: Optional['CliApp'] = None) -> CodeSignEntitlements:
        app_path = next((xcarchive_path.glob('Products/Applications/*.app')), None)
        if not app_path:
            raise IOError(f'Failed to obtain entitlements from {xcarchive_path}, .app not found')
        return cls.from_app(app_path, cli_app=cli_app)

    def get_icloud_container_environment(self) -> Optional[str]:
        return self.plist.get('com.apple.developer.icloud-container-environment')

    def get_icloud_services(self) -> List[str]:
        return self.plist.get('com.apple.developer.icloud-services', [])
