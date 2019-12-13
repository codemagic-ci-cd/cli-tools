from __future__ import annotations

import plistlib
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any
from typing import AnyStr
from typing import Dict
from typing import List
from typing import Union

from .byte_str_converter import BytesStrConverter
from .certificate import Certificate
from .json_serializable import JsonSerializable


class ProvisioningProfile(JsonSerializable, BytesStrConverter):
    DEFAULT_LOCATION = Path.home() / Path('Library', 'MobileDevice', 'Provisioning Profiles')

    def __init__(self, plist: Dict[str, Any]):
        self._plist = plist

    @classmethod
    def from_content(cls, content: AnyStr) -> ProvisioningProfile:
        plist: Dict[str, Any] = plistlib.loads(cls._bytes(content))
        return ProvisioningProfile(plist)

    @classmethod
    def from_path(cls, profile_path: Path) -> ProvisioningProfile:
        if not profile_path.exists():
            raise ValueError(f'Profile {profile_path} does not exist')
        profile_data = cls._read_profile(profile_path)
        plist: Dict[str, Any] = plistlib.loads(profile_data)
        return ProvisioningProfile(plist)

    @classmethod
    def _read_profile(cls, profile_path: Union[str, Path]) -> bytes:
        cmd = ['openssl', 'smime', '-inform', 'der', '-verify', '-noverify', '-in', str(profile_path)]
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except FileNotFoundError as nfe:
            raise EnvironmentError('OpenSSL executable not present on system') from nfe

        stdout, stderr = process.communicate(timeout=1)
        if process.returncode != 0:
            error = stderr.decode()
            raise ValueError(f'Invalid provisioning profile {profile_path}:\n{error}')
        return stdout

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
    def bundle_id(self):
        return '.'.join(self.application_identifier.split('.')[1:])

    @property
    def xcode_managed(self) -> bool:
        profile_name = self.name or ''
        fallback = profile_name.startswith('iOS Team Provisioning Profile:')
        return self._plist.get('IsXcodeManaged', fallback)

    @property
    def certificates(self) -> List[Certificate]:
        asn1_certificates = self._plist['DeveloperCertificates']
        return [Certificate.from_ans1(certificate) for certificate in asn1_certificates]

    @property
    def certificate_common_name(self) -> str:
        common_names = Counter(certificate.common_name for certificate in self.certificates)
        print(common_names)
        most_common = common_names.most_common(1)
        return most_common[0][0] if most_common else ''

    def dict(self) -> Dict:
        return {
            'name': self.name,
            'team_id': self.team_identifier,
            'team_name': self.team_name,
            'bundle_id': self.bundle_id,
            'specifier': self.uuid,
            'certificate_common_name': self.certificate_common_name,
            'xcode_managed': self.xcode_managed,
        }
