from __future__ import annotations

import pathlib
import plistlib
import shutil
import subprocess
import tempfile
import zipfile
from typing import Any
from typing import AnyStr
from typing import Dict
from typing import List

from codemagic.mixins import RunningCliAppMixin
from codemagic.mixins import StringConverterMixin
from codemagic.utilities import log


class CodeSignEntitlements(RunningCliAppMixin, StringConverterMixin):

    def __init__(self, entitlement_data: Dict[str, Any]):
        self.plist: Dict[str, Any] = entitlement_data
        self.logger = log.get_logger(self.__class__)

    @classmethod
    def _ensure_codesign(cls):
        if shutil.which('codesign') is None:
            raise IOError('Missing executable "codesign"')

    @classmethod
    def from_plist(cls, plist: AnyStr) -> CodeSignEntitlements:
        parsed_plist = plistlib.loads(cls._bytes(plist))
        return CodeSignEntitlements(parsed_plist)

    @classmethod
    def from_app(cls, app_path: pathlib.Path) -> CodeSignEntitlements:
        cls._ensure_codesign()
        cmd = ('codesign', '-d', '--entitlements', ':-', str(app_path))
        cli_app = cls.get_current_cli_app()
        try:
            if cli_app:
                process = cli_app.execute(cmd, show_output=False)
                process.raise_for_returncode()
                output = cls._bytes(process.stdout)
            else:
                output = subprocess.check_output(cmd, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as cpe:
            raise IOError(f'Failed to obtain entitlements from {app_path}, {cls._str(cpe.stderr)}')

        return cls.from_plist(output)

    @classmethod
    def from_ipa(cls, ipa_path: pathlib.Path) -> CodeSignEntitlements:
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
            return cls.from_app(app_path)

    @classmethod
    def from_xcarchive(cls, xcarchive_path: pathlib.Path) -> CodeSignEntitlements:
        app_path = next((xcarchive_path.glob('Products/Applications/*.app')), None)
        if not app_path:
            raise IOError(f'Failed to obtain entitlements from {xcarchive_path}, .app not found')
        return cls.from_app(app_path)

    def get_icloud_container_environments(self) -> List[str]:
        environment = self.plist.get('com.apple.developer.icloud-container-environment')
        if environment is None:
            return []
        elif isinstance(environment, str):
            return [environment]
        elif isinstance(environment, list):
            return environment
        raise ValueError(f'Unknown type for environment: {type(environment)}')

    def get_icloud_services(self) -> List[str]:
        return self.plist.get('com.apple.developer.icloud-services', [])
