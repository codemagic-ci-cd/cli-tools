from __future__ import annotations

import enum
import pathlib
import plistlib
import re
from dataclasses import dataclass
from typing import Counter
from typing import Dict
from typing import List
from typing import NoReturn
from typing import Optional
from typing import Sequence
from typing import Union
from typing import get_type_hints
from typing import overload

from codemagic.cli import Colors
from codemagic.utilities import log
from .matched_profile import MatchedProfile
from .provisioning_profile import ProvisioningProfile


class Destination(enum.Enum):
    EXPORT = 'export'
    UPLOAD = 'upload'


class ArchiveMethod(enum.Enum):
    AD_HOC = "ad-hoc"
    DEVELOPMENT = "development"
    APP_STORE = "app-store"
    ENTERPRISE = "enterprise"

    @classmethod
    def from_profiles(cls, profiles: Sequence[ProvisioningProfile]) -> ArchiveMethod:
        def is_development_profile(profile):
            return any(c.is_development_certificate for c in profile.certificates)

        enterprise_profiles = (p for p in profiles if p.provisions_all_devices)
        app_store_connect_compatible = (p for p in profiles if p.has_beta_entitlements)
        with_development_certificate = (p for p in profiles if is_development_profile(p))

        if any(enterprise_profiles):
            return ArchiveMethod.ENTERPRISE
        if any(app_store_connect_compatible):
            return ArchiveMethod.APP_STORE
        elif any(with_development_certificate):
            return ArchiveMethod.DEVELOPMENT
        else:
            return ArchiveMethod.AD_HOC


class SigningStyle(enum.Enum):
    AUTOMATIC = 'automatic'
    MANUAL = 'manual'

    @classmethod
    def from_profiles(cls, profiles: Sequence[ProvisioningProfile]) -> SigningStyle:
        xcode_managed_profiles = (pp for pp in profiles if pp.xcode_managed)
        if any(xcode_managed_profiles):
            return SigningStyle.AUTOMATIC
        else:
            return SigningStyle.MANUAL


@dataclass
class ProvisioningProfileInfo:
    identifier: str
    name: str


@dataclass
class Manifest:
    appURL: str
    displayImageURL: str
    fullSizeImageURL: str
    assetPackManifestURL: Optional[str] = None

    def dict(self) -> Dict[str, str]:
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class ExportOptions:
    compileBitcode: Optional[bool] = None
    destination: Optional[Destination] = None
    embedOnDemandResourcesAssetPacksInBundle: Optional[bool] = None
    generateAppStoreInformation: Optional[bool] = None
    iCloudContainerEnvironment: Optional[str] = None
    installerSigningCertificate: Optional[str] = None
    manifest: Optional[Manifest] = None
    method: Optional[ArchiveMethod] = None
    onDemandResourcesAssetPacksBaseURL: Optional[str] = None
    provisioningProfiles: Optional[List[ProvisioningProfileInfo]] = None
    signingCertificate: Optional[str] = None
    signingStyle: Optional[SigningStyle] = None
    stripSwiftSymbols: Optional[bool] = None
    teamID: Optional[str] = None
    thinning: Optional[str] = None
    uploadBitcode: Optional[bool] = None
    uploadSymbols: Optional[bool] = None

    def __post_init__(self):
        for field_name in self.__dict__:
            self.set_value(field_name, getattr(self, field_name))

    @classmethod
    def _get_field_type(cls, field_name: str) -> type:
        type_hint = get_type_hints(cls)[field_name]
        if hasattr(type_hint, '__origin__') and type_hint.__origin__ is Union:
            # Optionals are unions of actual type and NoneType
            actual_type = type_hint.__args__[0]
        else:
            # Literal type
            actual_type = type_hint
        return actual_type

    @overload
    def _set_manifest(self, new_manifest: Union[enum.Enum, bool, str, List[ProvisioningProfileInfo]]) -> NoReturn:
        ...

    @overload
    def _set_manifest(self, new_manifest: Union[Dict[str, str], Manifest]) -> None:
        ...

    def _set_manifest(self, new_manifest):
        if isinstance(new_manifest, Manifest):
            self.manifest = new_manifest
        elif isinstance(new_manifest, dict):
            try:
                self.manifest = Manifest(**new_manifest)
            except TypeError:
                raise ValueError(f'Invalid value for manifest: {new_manifest!r}')
        else:
            raise ValueError(f'Invalid value for manifest: {new_manifest!r}')

    @overload
    def _set_provisioning_profiles(self, new_profiles: Union[enum.Enum, bool, str, Manifest]) -> NoReturn:
        ...

    @overload
    def _set_provisioning_profiles(self, new_profiles: Union[Dict[str, str], List[ProvisioningProfileInfo]]) -> None:
        ...

    def _set_provisioning_profiles(self, new_profiles):
        if isinstance(new_profiles, list):
            if not all(isinstance(profile_info, ProvisioningProfileInfo) for profile_info in new_profiles):
                raise ValueError(f'Invalid value for provisioningProfiles: {new_profiles!r}')
            self.provisioningProfiles = new_profiles
        elif isinstance(new_profiles, dict):
            self.provisioningProfiles = [
                ProvisioningProfileInfo(identifier, name) for identifier, name in new_profiles.items()
            ]
        else:
            raise ValueError(f'Invalid value for provisioningProfiles: {new_profiles!r}')

    def set_value(self,
                  field_name: str,
                  value: Union[enum.Enum, bool, str, Dict[str, str], List[ProvisioningProfileInfo], Manifest]):

        if field_name not in self.__dict__:
            raise ValueError(f'Invalid filed {field_name}')

        field_type = self._get_field_type(field_name)
        if value is None:
            setattr(self, field_name, None)
        elif field_name == 'manifest':
            self._set_manifest(value)
        elif field_name == 'provisioningProfiles':
            self._set_provisioning_profiles(value)
        elif not isinstance(value, field_type):
            setattr(self, field_name, field_type(value))
        else:
            setattr(self, field_name, value)

    def update(self, **other_options):
        for field_name, value in other_options:
            self.set_value(field_name, value)

    @classmethod
    def from_path(cls, path: pathlib.Path) -> ExportOptions:
        with path.open('rb') as fd:
            data = plistlib.load(fd)  # type: ignore
        return ExportOptions(**data)

    @classmethod
    def from_matched_profiles(cls, matched_profiles: Sequence[MatchedProfile]) -> ExportOptions:
        used_profiles = [entry.profile for entry in matched_profiles]
        certificates = (c for mp in matched_profiles for c in mp.profile.certificates)
        team_ids = Counter[str](mp.profile.team_identifier for mp in matched_profiles)
        common_names = Counter[str](c.common_name.split(':')[0] for c in certificates)

        return ExportOptions(
            method=ArchiveMethod.from_profiles(used_profiles),
            signingStyle=SigningStyle.from_profiles(used_profiles),
            teamID=team_ids.most_common(1)[0][0] if team_ids else '',
            provisioningProfiles=[ProvisioningProfileInfo(mp.bundle_id, mp.profile.name) for mp in matched_profiles],
            signingCertificate=common_names.most_common(1)[0][0] if common_names else '',
        )

    def has_xcode_managed_profiles(self) -> bool:
        if not self.provisioningProfiles:
            return False
        return any(ProvisioningProfile.is_xcode_managed(pi.name) for pi in self.provisioningProfiles)

    def dict(self) -> Dict[str, Union[bool, str, Dict[str, str]]]:
        d = {
            field_name: value.value if isinstance(value, enum.Enum) else value
            for field_name, value in self.__dict__.items()
            if value is not None
        }
        if self.provisioningProfiles:
            d['provisioningProfiles'] = {p.identifier: p.name for p in self.provisioningProfiles}
        if self.manifest:
            d['manifest'] = self.manifest.dict()
        return d

    def save(self, path: pathlib.Path):
        with path.open('wb') as fd:
            plistlib.dump(self.dict(), fd)

    def notify(self):
        logger = log.get_logger(self.__class__)
        logger.info(Colors.GREEN('Generated options for exporting IPA'))
        options = self.dict()

        for key in sorted(options.keys()):
            value = options[key]
            option = re.sub(f'([A-Z])', r' \1', key.replace('ID', 'Id')).lstrip(' ').title()
            if isinstance(value, dict):
                logger.info(Colors.BLUE(f' - {option}:'))
                for k, v in value.items():
                    logger.info(Colors.BLUE(f'     - {k}: {v}'))
            else:
                logger.info(Colors.BLUE(f' - {option}: {value}'))
