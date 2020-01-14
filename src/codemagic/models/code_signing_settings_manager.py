from __future__ import annotations

import json
import pathlib
import shlex
import shutil
import subprocess
from functools import lru_cache
from tempfile import NamedTemporaryFile
from typing import Counter
from typing import Dict
from typing import List
from typing import Optional
from typing import TYPE_CHECKING

from codemagic.cli import Colors
from codemagic.mixins import StringConverterMixin
from codemagic.utilities import log
from .certificate import Certificate
from .export_options import ExportOptions
from .matched_profile import MatchedProfile
from .provisioning_profile import ProvisioningProfile

if TYPE_CHECKING:
    from codemagic.cli import CliApp


class CodeSigningSettingsManager(StringConverterMixin):

    def __init__(self, profiles: List[ProvisioningProfile], keychain_certificates: List[Certificate]):
        self.profiles: Dict[str, ProvisioningProfile] = {profile.uuid: profile for profile in profiles}
        self._certificates = keychain_certificates
        self._matched_profiles: List[MatchedProfile] = []
        self.logger = log.get_logger(self.__class__)

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

    def notify_profile_usage(self):
        self.logger.info(Colors.GREEN('Completed configuring code signing settings'))

        if not self._matched_profiles:
            message = 'Did not find matching provisioning profiles for code signing!'
            self.logger.warning(Colors.YELLOW(message))
            return

        for info in sorted(self._matched_profiles, key=lambda i: i.sort_key()):
            self.logger.info(Colors.BLUE(info.format()))

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

        self._matched_profiles.extend(
            MatchedProfile(profile=self.profiles[profile_uuid], **xcode_build_config)
            for profile_uuid, xcode_build_configs in used_profiles_info.items()
            for xcode_build_config in xcode_build_configs
        )

    def generate_export_options(self, custom_options: Optional[Dict]) -> ExportOptions:
        export_options = ExportOptions.from_matched_profiles(self._matched_profiles)
        export_options.update(**(custom_options or {}))
        return export_options
