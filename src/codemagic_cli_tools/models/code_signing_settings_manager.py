from __future__ import annotations

import enum
import json
import logging
import pathlib
import re
import shlex
import shutil
import subprocess
from functools import lru_cache
from tempfile import NamedTemporaryFile
from typing import Counter
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import TYPE_CHECKING
from typing import Union

from codemagic_cli_tools.cli import Colors
from codemagic_cli_tools.mixins import StringConverterMixin
from .certificate import Certificate
from .provisioning_profile import ProvisioningProfile

if TYPE_CHECKING:
    from codemagic_cli_tools.cli import CliApp


ExportOptions = Dict[str, Union[str, Dict[str, str]]]


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


class CodeSigningSettingsManager(StringConverterMixin):

    def __init__(self, profiles: List[ProvisioningProfile], keychain_certificates: List[Certificate]):
        self.profiles: Dict[str, ProvisioningProfile] = {profile.uuid: profile for profile in profiles}
        self._certificates = keychain_certificates
        self._modified_build_configs_info: List[Dict] = []
        self._used_profiles: Dict[str, ProvisioningProfile] = {}

    @lru_cache()
    def _get_json_serialized_profiles(self) -> str:
        profiles = [self._serialize_profile(p) for p in self.profiles.values()]
        return json.dumps(profiles)

    def _serialize_profile(self, profile):
        usable_certificates = profile.get_usable_certificates(self._certificates)
        common_names = Counter[str](certificate.common_name for certificate in usable_certificates)
        most_popular_common = common_names.most_common(1)
        common_name = most_popular_common[0][0] if most_popular_common else ''
        return {
            'certificate_common_name': common_name,
            'name': profile.name,
            'team_id': profile.team_identifier,
            'team_name': profile.team_name,
            'bundle_id': profile.bundle_id,
            'specifier': profile.uuid,
            'xcode_managed': profile.xcode_managed,
            'certificates': [c.serial for c in profile.certificates],
        }

    @property
    def _code_signing_manager(self) -> str:
        if shutil.which('code_signing_manager.rb'):
            return 'code_signing_manager.rb'
        executable = pathlib.Path(__file__) / '..' / '..' / '..' / '..' / 'bin' / 'code_signing_manager.rb'
        return str(executable.resolve())

    @classmethod
    def _format_build_config_meta(cls, build_config_info):
        profile = build_config_info['profile']
        project = build_config_info['project_name']
        target = build_config_info['target_name']
        config = build_config_info['build_configuration']
        return Colors.BLUE(
            f' - Using profile "{profile.name}" [{profile.uuid}] '
            f'for target "{target}" [{config}] from project "{project}"'
        )

    def _sort_modified_build_configs_info(self):
        def key(info):
            return info['project_name'], info['target_name'], info['build_configuration']

        self._modified_build_configs_info.sort(key=key)

    def notify_profile_usage(self, logger: Optional[logging.Logger]):
        if logger is None:
            logger = logging.getLogger(self.__class__.__name__)

        logger.info(Colors.GREEN('Completed configuring code signing settings'))

        if not self._modified_build_configs_info:
            message = 'Did not find matching provisioning profiles for code signing!'
            logger.warning(Colors.YELLOW(message))
            return

        self._sort_modified_build_configs_info()
        for build_config_info in self._modified_build_configs_info:
            logger.info(self._format_build_config_meta(build_config_info))

    def notify_export_options(self, options: ExportOptions, logger: Optional[logging.Logger]):
        if logger is None:
            logger = logging.getLogger(self.__class__.__name__)

        logger.info(Colors.GREEN('Generated options for exporting IPA'))
        for key in sorted(options):
            value = options[key]
            option = re.sub(f'([A-Z])', r' \1', key.replace('ID', 'Id')).lstrip(' ').title()
            if isinstance(value, dict):
                logger.info(Colors.BLUE(f' - {option}:'))
                for k, v in value.items():
                    logger.info(Colors.BLUE(f'     - {k}: {v}'))
            else:
                logger.info(Colors.BLUE(f' - {option}: {value}'))

    def _apply(self, xcode_project, result_file_name, cli_app):
        cmd = [
            self._code_signing_manager,
            '--xcode-project', xcode_project,
            '--used-profiles', result_file_name,
            '--profiles', self._get_json_serialized_profiles(),
        ]
        if cli_app and cli_app.verbose:
            cmd.append('--verbose')

        process = None
        try:
            if cli_app:
                process = cli_app.execute(cmd)
                process.raise_for_returncode()
            else:
                subprocess.check_output(cmd, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            xcode_project = shlex.quote(str(xcode_project))
            raise IOError(f'Failed to set code signing settings for {xcode_project}', process)

    def use_profiles(self, xcode_project: pathlib.Path, *, cli_app: Optional['CliApp'] = None):
        with NamedTemporaryFile(mode='r', prefix='used_profiles_', suffix='.json') as used_profiles:
            self._apply(xcode_project, used_profiles.name, cli_app)
            try:
                used_profiles_info = json.load(used_profiles)
            except ValueError:
                used_profiles_info = {}

        self._modified_build_configs_info.extend(
            {'profile': self.profiles[profile_uuid], **xcode_build_config}
            for profile_uuid, xcode_build_configs in used_profiles_info.items()
            for xcode_build_config in xcode_build_configs
        )
        self._used_profiles.update({
            profile_uuid: self.profiles[profile_uuid] for profile_uuid, _ in used_profiles_info.items()
        })

    def generate_export_options(self, custom_options) -> ExportOptions:
        used_profiles = [entry['profile'] for entry in self._modified_build_configs_info]
        export_options = {
            'method': ArchiveMethod.from_profiles(used_profiles).value,
            'signingStyle': SigningStyle.from_profiles(used_profiles).value,
            'teamID': self._get_export_team_id(),
            'provisioningProfiles': self._get_export_profiles(),
            'signingCertificate': self._get_export_certificate(),
        }
        if custom_options:
            export_options.update(custom_options)
        return export_options

    def _get_export_team_id(self) -> str:
        identifiers = Counter[str](p.team_identifier for p in self._used_profiles.values())
        if not identifiers:
            return ''
        return identifiers.most_common(1)[0][0]

    def _get_export_profiles(self) -> Dict[str, str]:
        return {
            entry['bundle_id']: entry['profile'].name
            for entry in self._modified_build_configs_info
        }

    def _get_export_certificate(self) -> str:
        certificates = (c for p in self._used_profiles.values() for c in p.certificates)
        common_names = Counter[str](c.common_name.split(':')[0] for c in certificates)
        if not common_names:
            return ''
        return common_names.most_common(1)[0][0]
