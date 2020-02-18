from __future__ import annotations

import plistlib
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any
from typing import AnyStr
from typing import Dict
from typing import Generator
from typing import List
from typing import Optional
from typing import Sequence
from typing import TYPE_CHECKING
from typing import Union

from codemagic.mixins import StringConverterMixin
from codemagic.models.certificate import Certificate
from codemagic.models.json_serializable import JsonSerializable

if TYPE_CHECKING:
    from codemagic.cli import CliApp


class ProvisioningProfile(JsonSerializable, StringConverterMixin):
    DEFAULT_LOCATION = Path.home() / Path('Library', 'MobileDevice', 'Provisioning Profiles')

    def __init__(self, plist: Dict[str, Any]):
        self._plist = plist

    @classmethod
    def from_content(cls, content: AnyStr) -> ProvisioningProfile:
        plist: Dict[str, Any] = plistlib.loads(cls._bytes(content))
        return ProvisioningProfile(plist)

    @classmethod
    def from_path(cls, profile_path: Path, *, cli_app: Optional['CliApp'] = None) -> ProvisioningProfile:
        if not profile_path.exists():
            raise ValueError(f'Profile {profile_path} does not exist')
        profile_data = cls._read_profile(profile_path, cli_app)
        plist: Dict[str, Any] = plistlib.loads(profile_data)
        return ProvisioningProfile(plist)

    @classmethod
    def _ensure_openssl(cls):
        if shutil.which('openssl') is None:
            raise IOError('OpenSSL executable not present on system')

    @classmethod
    def _read_profile(cls, profile_path: Union[str, Path], cli_app: Optional['CliApp']) -> bytes:
        cls._ensure_openssl()
        cmd = ('openssl', 'smime', '-inform', 'der', '-verify', '-noverify', '-in', str(profile_path))
        try:
            if cli_app:
                process = cli_app.execute(cmd, show_output=False)
                process.raise_for_returncode()
                converted = cls._bytes(process.stdout)
            else:
                stdout = subprocess.check_output(cmd, stderr=subprocess.PIPE)
                converted = cls._bytes(stdout)
        except subprocess.CalledProcessError as cpe:
            raise ValueError(
                f'Invalid provisioning profile {profile_path}:\n{cls._str(cpe.stderr)}')
        return converted

    @property
    def name(self) -> str:
        return self._plist['Name']

    @property
    def uuid(self) -> str:
        return self._plist['UUID']

    @property
    def team_identifier(self) -> str:
        return self._plist.get('TeamIdentifier', [None])[0]

    @property
    def team_name(self) -> str:
        return self._plist.get('TeamName', '')

    @property
    def has_beta_entitlements(self) -> bool:
        return self._plist.get('Entitlements', dict()).get('beta-reports-active', False)

    @property
    def provisioned_devices(self) -> List[str]:
        return self._plist.get("ProvisionedDevices", [])

    @property
    def provisions_all_devices(self) -> bool:
        return self._plist.get("ProvisionsAllDevices", False)

    @property
    def application_identifier(self) -> str:
        return self._plist.get('Entitlements', dict()).get("application-identifier", '')

    @property
    def is_wildcard(self) -> bool:
        return self.application_identifier.endswith("*")

    @property
    def bundle_id(self) -> str:
        return '.'.join(self.application_identifier.split('.')[1:])

    @property
    def xcode_managed(self) -> bool:
        fallback = self.is_xcode_managed(self.name or '')
        return self._plist.get('IsXcodeManaged', fallback)

    @property
    def certificates(self) -> List[Certificate]:
        asn1_certificates = self._plist['DeveloperCertificates']
        return [Certificate.from_ans1(certificate) for certificate in asn1_certificates]

    def dict(self) -> Dict:
        return {
            'application_identifier': self.application_identifier,
            'bundle_id': self.bundle_id,
            'certificates': [c.dict() for c in self.certificates],
            'has_beta_entitlements': self.has_beta_entitlements,
            'is_wildcard': self.is_wildcard,
            'name': self.name,
            'provisioned_devices': self.provisioned_devices,
            'provisions_all_devices': self.provisions_all_devices,
            'team_identifier': self.team_identifier,
            'team_name': self.team_name,
            'uuid': self.uuid,
            'xcode_managed': self.xcode_managed,
        }

    def get_usable_certificates(self, certificates: Sequence[Certificate]) -> Generator[Certificate, None, None]:
        available_certificates_serials = {c.serial for c in certificates}
        return (c for c in self.certificates if c.serial in available_certificates_serials)

    @classmethod
    def is_xcode_managed(cls, profile_name: str) -> bool:
        xcode_managed_profile_name_patt = re.compile(r'^iOS Team ((Ad Hoc|Store) )?Provisioning Profile:')
        xcode_managed_name_match = xcode_managed_profile_name_patt.match(profile_name)
        return xcode_managed_name_match is not None
