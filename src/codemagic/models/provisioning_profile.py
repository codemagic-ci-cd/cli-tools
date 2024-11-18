from __future__ import annotations

import pathlib
import plistlib
import re
import shutil
import subprocess
from datetime import datetime
from datetime import timezone
from tempfile import NamedTemporaryFile
from typing import Any
from typing import AnyStr
from typing import Dict
from typing import Generator
from typing import List
from typing import Sequence
from typing import Union

from codemagic.mixins import RunningCliAppMixin
from codemagic.mixins import StringConverterMixin
from codemagic.models.certificate import Certificate
from codemagic.models.json_serializable import JsonSerializable


class ProvisioningProfile(JsonSerializable, RunningCliAppMixin, StringConverterMixin):
    DEFAULT_LOCATION = pathlib.Path(pathlib.Path.home(), "Library", "MobileDevice", "Provisioning Profiles")

    def __init__(self, plist: Dict[str, Any]):
        self._plist = plist

    @classmethod
    def from_content(cls, content: AnyStr) -> ProvisioningProfile:
        with NamedTemporaryFile(mode="wb") as tf:
            tf.write(cls._bytes(content))
            tf.flush()
            profile_data = cls._read_profile(tf.name)
        plist: Dict[str, Any] = plistlib.loads(profile_data)
        return ProvisioningProfile(plist)

    @classmethod
    def from_path(cls, profile_path: Union[pathlib.Path, AnyStr]) -> ProvisioningProfile:
        if isinstance(profile_path, (bytes, str)):
            profile_path = pathlib.Path(cls._str(profile_path))

        if not profile_path.exists():
            raise ValueError(f"Profile {profile_path} does not exist")

        profile_data = cls._read_profile(profile_path)
        plist: Dict[str, Any] = plistlib.loads(profile_data)
        return ProvisioningProfile(plist)

    @classmethod
    def _ensure_openssl(cls):
        if shutil.which("openssl") is None:
            raise IOError("OpenSSL executable is not present on system")

    @classmethod
    def _read_profile(cls, profile_path: Union[pathlib.Path, AnyStr]) -> bytes:
        if isinstance(profile_path, pathlib.Path):
            profile_path_arg = str(profile_path)
        else:
            profile_path_arg = cls._str(profile_path)

        cls._ensure_openssl()
        cmd = ("openssl", "smime", "-inform", "der", "-verify", "-noverify", "-in", profile_path_arg)
        cli_app = cls.get_current_cli_app()
        try:
            if cli_app:
                process = cli_app.execute(cmd, show_output=False)
                process.raise_for_returncode()
                converted = cls._bytes(process.stdout)
            else:
                stdout = subprocess.check_output(cmd, stderr=subprocess.PIPE)
                converted = cls._bytes(stdout)
        except subprocess.CalledProcessError as cpe:
            raise ValueError(f"Invalid provisioning profile {profile_path_arg}:\n{cls._str(cpe.stderr)}")
        return converted

    @property
    def name(self) -> str:
        return self._plist["Name"]

    @property
    def uuid(self) -> str:
        return self._plist["UUID"]

    @property
    def team_identifier(self) -> str:
        team_identifiers = self._plist.get("TeamIdentifier") or [""]
        return team_identifiers[0]

    @property
    def team_name(self) -> str:
        return self._plist.get("TeamName", "")

    @property
    def has_beta_entitlements(self) -> bool:
        entitlements = self._plist.get("Entitlements", dict())
        for key, value in entitlements.items():
            if "beta-reports-active" in key:
                return value
        return False

    @property
    def provisioned_devices(self) -> List[str]:
        return self._plist.get("ProvisionedDevices", [])

    @property
    def provisions_all_devices(self) -> bool:
        return self._plist.get("ProvisionsAllDevices", False)

    @property
    def application_identifier(self) -> str:
        entitlements = self._plist.get("Entitlements", dict())
        for key, value in entitlements.items():
            if "application-identifier" not in key:
                continue
            elif "associated-application-identifier" in key:
                continue
            elif isinstance(value, str):
                return value
        return ""

    @property
    def is_wildcard(self) -> bool:
        return self.application_identifier.endswith("*")

    @property
    def bundle_id(self) -> str:
        return ".".join(self.application_identifier.split(".")[1:])

    @property
    def xcode_managed(self) -> bool:
        fallback = self.is_xcode_managed(self.name or "")
        return self._plist.get("IsXcodeManaged", fallback)

    @property
    def certificates(self) -> List[Certificate]:
        asn1_certificates = self._plist["DeveloperCertificates"]
        return [Certificate.from_ans1(certificate) for certificate in asn1_certificates]

    @property
    def creation_date(self) -> datetime:
        # Timezone information is lost when plist is parsed with plistlib.
        # Originally dates are in UTC in profile files.
        dt = self._plist["CreationDate"]
        return dt.replace(tzinfo=timezone.utc)

    @property
    def expiration_date(self) -> datetime:
        # Timezone information is lost when plist is parsed with plistlib.
        # Originally dates are in UTC in profile files.
        dt = self._plist["ExpirationDate"]
        return dt.replace(tzinfo=timezone.utc)

    def dict(self) -> Dict:
        return {
            "application_identifier": self.application_identifier,
            "bundle_id": self.bundle_id,
            "certificates": [c.dict() for c in self.certificates],
            "has_beta_entitlements": self.has_beta_entitlements,
            "is_wildcard": self.is_wildcard,
            "name": self.name,
            "provisioned_devices": self.provisioned_devices,
            "provisions_all_devices": self.provisions_all_devices,
            "team_identifier": self.team_identifier,
            "team_name": self.team_name,
            "uuid": self.uuid,
            "xcode_managed": self.xcode_managed,
        }

    def get_usable_certificates(self, certificates: Sequence[Certificate]) -> Generator[Certificate, None, None]:
        available_certificates_serials = {c.serial for c in certificates}
        return (c for c in self.certificates if c.serial in available_certificates_serials)

    @classmethod
    def is_xcode_managed(cls, profile_name: str) -> bool:
        xcode_managed_profile_name_patt = re.compile(r"^iOS Team ((Ad Hoc|Store) )?Provisioning Profile:")
        xcode_managed_name_match = xcode_managed_profile_name_patt.match(profile_name)
        return xcode_managed_name_match is not None
